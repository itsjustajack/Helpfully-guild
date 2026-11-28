#!/usr/bin/env python3
"""Run blender-* skill scripts on Patch's cloud Blender (patch.gg/blender) through the pch CLI.

Host-side (system Python 3.9+, no bpy). Needs pch signed in (`pch login`). Sessions cost credits
while they run (1 credit = $0.01; `pch blender prices`), pause themselves when idle and keep /work.
A session is a live Blender: the scene stays between calls, as in an MCP session, and the person
can watch it on patch.gg/blender. Local paths in the arguments are sent to the session's /work at
the same place relative to this folder, and files a call writes come back here the same way.

Usage:
  python cloud.py run [--blend in.blend] [--process] [--upload PATH]... SCRIPT.py [-- args]
  python cloud.py expr "import bpy; print(len(bpy.data.objects))"
  python cloud.py exec "ffmpeg -i render/f_%04d.png clip.mp4"   # a shell command in /work
  python cloud.py look [-o look.jpg] [--angles 4] [--engine eevee] [--camera Cam]
  python cloud.py render [scene.blend] [-o renders/] [--frames 1-120] [--video mp4]
      [--engine eevee|cycles] [--gpu l40s|l4] [--max-cost 40]   # no .blend: the session's scene
  python cloud.py fork [--count 3]      # copies of the session to try things side by side
  python cloud.py push PATH...  |  pull PATH...  |  status  |  stop
  python cloud.py start [--size small|medium|large] [--gpu l4|l40s] [--name NAME]
Common flags: --session ses_... (default: the one saved in .cloud-blender.json here, else a new
one), --timeout SECONDS (600), --no-pull. Env: PCH (path to pch), PCH_ENV, PCH_CONFIG.
Prints JSON (run: the script's own JSON plus a "cloud" key). Exit: 0 ok, 1 failed, 2 no pch or
not signed in, 3 stopped at --max-cost.
"""
import argparse
import hashlib
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path, PurePosixPath

HERE = Path(__file__).resolve().parent
SKILLS = HERE.parents[1]                      # .../skills (or ~/.claude/skills when installed)
STATE = ".cloud-blender.json"
REMOTE_SKILLS = "_skills"                     # /work/_skills/<skill>/scripts/...
REMOTE_IN = "_in"                             # inputs from outside this folder
REMOTE_RUNS = "_runs"                         # logs of --process runs that failed
SKIP_PULL = (REMOTE_SKILLS + "/", REMOTE_IN + "/", REMOTE_RUNS + "/", ".patch/", "_render/", "__pycache__/")
MARK = "@@JSON@@"
BLENDER_LIB = "/opt/blender/lib"              # cloud image layout (Blender 5.2.0)

# Runs inside the session's Blender (pch blender run). Executes a skill script exactly as
# `blender -b -P script.py -- args` would, in the live scene, and returns its @@JSON@@ lines.
LIVE = r'''
import contextlib, ctypes, io, json, os, runpy, sys, traceback
a = args
os.chdir("/work")
try:  # Blender 5.2.0's glTF meshopt bridge can't find this library on its own
    ctypes.CDLL(a["lib"] + "/libmeshoptimizer.so", mode=ctypes.RTLD_GLOBAL)
except OSError:
    pass
root = "/work/" + a["skills"] + "/"
for k in [k for k, m in list(sys.modules.items()) if (getattr(m, "__file__", None) or "").startswith(root)]:
    del sys.modules[k]  # fresh skill code every call, like a new process
sd = os.path.dirname(a["script"])
if sd not in sys.path:
    sys.path.insert(0, sd)
old, sys.argv = sys.argv, [sys.argv[0], "--", *a["argv"]]
buf, code, err = io.StringIO(), 0, None
try:
    with contextlib.redirect_stdout(buf):
        runpy.run_path(a["script"], run_name="__main__")
except SystemExit as e:
    code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
except BaseException:
    code, err = 1, traceback.format_exc()[-3000:]
finally:
    sys.argv = old
out = buf.getvalue().splitlines()
js = [json.loads(l[len(a["mark"]):]) for l in out if l.startswith(a["mark"])]
result = {"code": code, "json": js, "error": err, "tail": [] if js else out[-20:]}
'''

EXPR = r'''
import contextlib, io, os
os.chdir("/work")
buf, ns = io.StringIO(), {"__name__": "__cloud_expr__"}
with contextlib.redirect_stdout(buf):
    exec(compile(args["code"], "<expr>", "exec"), ns)
result = {"stdout": buf.getvalue()[-20000:], "result": ns.get("result")}
'''

PACK = r'''
import os, bpy  # (not 'import bpy' first: tools/sync_shared.py would take this for a Blender script)
os.makedirs(os.path.dirname(args["path"]), exist_ok=True)
try:
    bpy.ops.file.pack_all()
except RuntimeError:
    pass
bpy.ops.wm.save_as_mainfile(filepath=args["path"], copy=True)
sc = bpy.context.scene
result = {"frames": [sc.frame_start, sc.frame_end], "engine": sc.render.engine,
          "res": [sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage]}
'''


class CloudError(Exception):
    def __init__(self, msg, code=1, details=None):
        super().__init__(msg)
        self.code, self.details = code, details


# ---------------------------------------------------------------- pch

def pch_cmd():
    exe = os.environ.get("PCH") or shutil.which("pch")
    if not exe:
        raise CloudError("pch not found. Install it (https://patch.gg/llms.txt has the one-line "
                         "installer, or npm i -g @patchgg/cli), then run `pch login`; or set PCH.", 2)
    return [exe]


def pch(*args, timeout=None, ok=(0,), retries=0):
    """Run `pch --json ...`; return (exit code, parsed stdout). Raise on codes not in ok, and on any failing
    exit that printed nothing. retries: how often to try again after a dropped connection (only for calls
    that are safe to repeat)."""
    cmd = pch_cmd() + ["--json", *[str(a) for a in args]]
    for attempt in range(retries + 1):
        try:
            p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                               timeout=timeout)
        except subprocess.TimeoutExpired:
            raise CloudError(f"pch {' '.join(map(str, args[:3]))} gave no answer in {timeout} s")
        data = None
        if p.stdout.strip():
            try:
                data = json.loads(p.stdout)
            except ValueError:
                data = {"text": p.stdout[-4000:]}
        if os.environ.get("BAS_CLOUD_DEBUG"):  # a file to log every pch call to (no secrets: replies only)
            with open(os.environ["BAS_CLOUD_DEBUG"], "a", encoding="utf-8") as f:
                f.write(json.dumps({"t": round(time.time(), 1), "args": [str(a) for a in args][:8], "exit": p.returncode,
                                    "out": p.stdout[:300] + " ... " + p.stdout[-300:], "err": p.stderr[-300:]}) + "\n")
        if p.returncode in ok and (data is not None or p.returncode == 0):
            return p.returncode, data
        err = None
        for line in reversed(p.stderr.splitlines()):
            try:
                j = json.loads(line)
            except ValueError:
                continue
            if isinstance(j, dict) and "error" in j:
                err = j["error"]
                break
        msg = (err or {}).get("message") if isinstance(err, dict) else None
        code = 2 if p.returncode == 4 else (3 if p.returncode == 3 else 1)
        e = CloudError(msg or (p.stderr.strip().splitlines() or ["pch failed"])[-1], code,
                       {"pch_exit": p.returncode, "args": [str(a) for a in args[:4]], "error": err})
        if attempt < retries and transient(e):
            time.sleep(4 * (attempt + 1))
            continue
        raise e


def transient(e):
    """A dropped connection to a session (the work goes on there) or a session still waking up."""
    err = (e.details or {}).get("error") or {}
    return (err.get("code") in ("session_unreachable", "session_not_ready", "upload_failed")
            or any(w in str(e) for w in ("fetch failed", "timed out", "ENETUNREACH", "ECONNRESET")))


# ---------------------------------------------------------------- state + session

def load_state(d):
    try:
        return json.loads((d / STATE).read_text("utf-8"))
    except (OSError, ValueError):
        return {}


def save_state(d, st):
    (d / STATE).write_text(json.dumps(st, indent=1) + "\n", "utf-8")


def start_session(o, st):
    a = ["blender", "session", "start", "--wait", "120",
         "--name", o.name or f"{o.dir.name} · blender skills"]
    if getattr(o, "size", None):
        a += ["--size", o.size]
    if getattr(o, "gpu", None):
        a += ["--gpu", o.gpu]
    _, s = pch(*a, ok=(0, 7), timeout=300)
    st["session"] = s["id"]
    save_state(o.dir, st)
    return s["id"]


def session(o, st):
    """The session to use: --session, the saved one if it's still alive, or a new one."""
    if o.session:
        return o.session  # an explicit session never replaces the one saved here
    sid = st.get("session")
    if sid:
        try:
            _, s = pch("blender", "session", "view", sid, timeout=60, retries=2)
            if s.get("state") not in ("stopped", "failed", "error") and s.get("desired_state") != "stopped":
                return sid
        except CloudError:
            pass
    return start_session(o, st)


def skill_files():
    files = []
    for d in sorted(SKILLS.glob("blender-*")):
        for sub in ("scripts", "assets"):
            for f in sorted((d / sub).rglob("*")):
                if f.is_file() and "__pycache__" not in f.parts and f.suffix != ".pyc":
                    files.append(f)
    return files


def sync_skills(o, sid, st):
    """Send the blender-* skills' scripts to /work/_skills once per session (again when they change)."""
    files = skill_files()
    h = hashlib.sha256()
    for f in files:
        h.update(str(f.relative_to(SKILLS)).encode())
        h.update(f.read_bytes())
    digest = h.hexdigest()[:16]
    synced = st.setdefault("synced", {})
    if synced.get(sid) == digest:
        return
    with tempfile.TemporaryDirectory(prefix="bas_skills_") as tmp:
        for f in files:
            dst = Path(tmp) / f.relative_to(SKILLS)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dst)
        pch("blender", "files", "upload", sid, tmp, "--to", REMOTE_SKILLS + "/", timeout=900, retries=2)
    fresh = load_state(o.dir)                     # another call may have written it meanwhile
    synced = {**fresh.get("synced", {}), **st.get("synced", {}), sid: digest}
    st["synced"] = synced
    if "session" not in st and fresh.get("session"):
        st["session"] = fresh["session"]
    save_state(o.dir, st)


# ---------------------------------------------------------------- files

def remote_for(o, p):
    """Where a local path lives in /work: same place relative to this folder, else _in/<name>."""
    p = Path(p).resolve()
    try:
        return PurePosixPath(*p.relative_to(o.dir).parts).as_posix()
    except ValueError:
        return f"{REMOTE_IN}/{p.name}"


def upload(o, sid, paths):
    """Send local files/folders to the session, each to remote_for(path). Returns {local: remote}."""
    groups, mapping = {}, {}
    for p in paths:
        p = Path(p)
        r = remote_for(o, p)
        mapping[str(p)] = r
        parent = str(PurePosixPath(r).parent)
        if p.is_dir():
            groups.setdefault((r.rstrip("/") + "/", True), []).append(p)
        else:
            groups.setdefault(("" if parent == "." else parent + "/", False), []).append(p)
    for (to, _is_dir), srcs in groups.items():
        a = ["blender", "files", "upload", sid, *map(str, srcs)]
        if to:
            a += ["--to", to]
        pch(*a, timeout=1800, retries=2)
    return mapping


def is_local_path(tok):
    if tok.startswith(("-", "//")) or "://" in tok or "\n" in tok or len(tok) > 400:
        return False
    if not any(c in tok for c in "/\\.") or tok in (".", ".."):
        return False
    try:
        return Path(tok).exists()
    except OSError:
        return False


def snapshot(sid):
    files, after = {}, None
    while True:
        a = ["blender", "files", "ls", sid, "--limit", "1000"] + (["--after", after] if after else [])
        _, d = pch(*a, timeout=120, retries=3)
        page = d.get("files", [])
        for f in page:
            files[f["path"]] = (f.get("size"), f.get("modified_at"))
        after = d.get("next")
        total = d.get("count")
        if not page or not after or (len(files) >= total if total else len(page) < 1000):
            return files


def pull(o, sid, paths, limit_mb=None):
    """Fetch /work paths into this folder at the same places, replacing what's there."""
    paths = [p for p in paths if p]
    if not paths:
        return [], []
    with tempfile.TemporaryDirectory(prefix="bas_pull_") as tmp:
        _, d = pch("blender", "files", "download", sid, *paths, "-o", tmp, timeout=3600, retries=2)
        got = []
        for r in (d or {}).get("downloaded", []) + (d or {}).get("unchanged", []):
            src = Path(tmp) / r
            if src.is_file():
                dst = o.dir / r
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(dst))
                got.append(r)
        refused = [str(x) for x in (d or {}).get("refused", []) + (d or {}).get("missing", [])]
    return got, refused


def pull_changed(o, sid, before, after, limit_mb):
    changed = sorted(p for p, v in after.items()
                     if before.get(p) != v and not p.startswith(SKIP_PULL))
    take, left, total = [], [], 0
    for p in changed:
        size = after[p][0] or 0
        if total + size > limit_mb * 1e6:
            left.append(p)
        else:
            take.append(p)
            total += size
    got, refused = pull(o, sid, take) if take else ([], [])
    return got, left + refused


# ---------------------------------------------------------------- commands

def wait_run(sid, first, timeout):
    """Follow a run/exec until it ends, in short waits: one long wait can drop ("fetch failed") while the
    work goes on in the session."""
    data, deadline = first, time.time() + timeout + 300
    run = (first or {}).get("run")
    while data and (data.get("timed_out") or data.get("status") == "running") and run and time.time() < deadline:
        try:
            _, nxt = pch("blender", "runs", "view", sid, run, "--wait", "45", ok=(0, 1, 7), timeout=150)
        except CloudError as e:
            if not transient(e):
                raise
            time.sleep(5)
            continue
        if nxt:  # an empty answer: ask again
            data = nxt
        else:
            time.sleep(3)
    return data


def start(sid, kind, args, timeout):
    """Start `pch blender run|exec` and follow it to its end. If the start itself drops, find the run that
    began anyway (an exec by its exact command) before trying once more."""
    t0 = time.time()
    call = ["blender", kind, sid, "--timeout-s", timeout, "--wait", "20", *args]
    try:
        _, d = pch(*call, ok=(0, 1, 7), timeout=240)
    except CloudError as e:
        if not transient(e):
            raise
        time.sleep(3)
        d = adopt(sid, kind, t0, args)
        if d is None:
            _, d = pch(*call, ok=(0, 1, 7), timeout=240)
    return wait_run(sid, d, timeout)


def adopt(sid, kind, since, args):
    """The run this call started, if it started: same kind, begun since, and for an exec the same command.
    A live run can't be told apart from another by its reply, so it's taken only when it's the one unread."""
    from datetime import datetime
    try:
        _, d = pch("blender", "runs", "list", sid, timeout=60, retries=2)
    except CloudError:
        return None
    found = []
    for r in (d or {}).get("runs", []):
        try:
            ts = datetime.fromisoformat((r.get("started_at") or "").replace("Z", "+00:00")).timestamp()
        except ValueError:
            continue
        if r.get("kind") == kind and ts >= since - 15 and not r.get("read"):
            found.append(r)
    want = args[0] if kind == "exec" and len(args) == 1 else None
    for r in found:
        try:
            _, v = pch("blender", "runs", "view", sid, r["run"], "--wait", "0", ok=(0, 1, 7), timeout=60, retries=1)
        except CloudError:
            continue
        v = v or {}
        v.setdefault("run", r["run"])
        if want is not None and v.get("command") == want:
            return v
        if kind == "run" and len(found) == 1:
            return v
    return None


def cmd_run(o, st):
    sid = session(o, st)
    sync_skills(o, sid, st)
    script = Path(o.script).resolve()
    try:
        rscript = f"{REMOTE_SKILLS}/{script.relative_to(SKILLS).as_posix()}"
    except ValueError:
        rscript = upload(o, sid, [script])[str(script)]
    argv, sends = [], list(o.upload or [])
    for tok in o.args:
        if is_local_path(tok):
            sends.append(tok)
            argv.append(remote_for(o, tok))
        else:
            argv.append(tok)
    blend = None
    if o.blend:
        if Path(o.blend).exists():
            sends.append(o.blend)
            blend = remote_for(o, o.blend)
        else:
            blend = o.blend  # already in /work
    if sends:
        upload(o, sid, sends)
    before = snapshot(sid) if not o.no_pull else {}
    if o.process:
        cmd = ["env", f"LD_LIBRARY_PATH={BLENDER_LIB}", "blender", "-b"] + ([blend] if blend else [])
        cmd += ["--factory-startup", "--python-exit-code", "1", "-P", rscript, "--", *argv]
        # Blender's own log goes to a file: a long render's log can crowd the result out of the reply
        base = f"{REMOTE_RUNS}/{time.strftime('%Y%m%d-%H%M%S')}-{os.getpid()}"
        log, res_f = base + ".log", base + ".json"
        sh = (f"mkdir -p {REMOTE_RUNS} && {' '.join(shlex.quote(c) for c in cmd)} > {log} 2>&1; rc=$?; "
              f"grep '^{MARK}' {log} | tee {res_f}; "
              f"if [ $rc -ne 0 ]; then tail -n 30 {log} >&2; else rm -f {log}; fi; exit $rc")
        d = start(sid, "exec", [sh], o.timeout)
        out = (d or {}).get("stdout") or ""
        try:
            js = [json.loads(l[len(MARK):]) for l in out.splitlines() if l.startswith(MARK)]
        except ValueError:  # the reply cuts long output short: read the results from the session's file
            with tempfile.TemporaryDirectory(prefix="bas_res_") as tmp:
                pch("blender", "files", "download", sid, res_f, "-o", tmp, timeout=600, retries=2)
                text = (Path(tmp) / res_f).read_text("utf-8")
            js = [json.loads(l[len(MARK):]) for l in text.splitlines() if l.startswith(MARK)]
        res = {"code": (d or {}).get("exit_code", 1), "json": js, "error": None,
               "tail": [] if js else ((d or {}).get("stderr") or out).splitlines()[-20:]}
    else:
        if blend:
            pch("blender", "open", sid, blend, "--timeout-s", 120, timeout=300)
        with tempfile.TemporaryDirectory(prefix="bas_run_") as tmp:
            code_f, args_f = Path(tmp) / "live.py", Path(tmp) / "args.json"
            code_f.write_text(LIVE, "utf-8")
            args_f.write_text(json.dumps({"script": "/work/" + rscript, "argv": argv, "mark": MARK,
                                          "skills": REMOTE_SKILLS, "lib": BLENDER_LIB}), "utf-8")
            d = start(sid, "run", [str(code_f), "--args", "@" + str(args_f)], o.timeout)
        res = (d or {}).get("result") or {"code": 1, "json": [], "error": (d or {}).get("stderr"),
                                          "tail": ((d or {}).get("stdout") or "").splitlines()[-20:]}
    info = {"session": sid, "mode": "process" if o.process else "live",
            "spent": ((d or {}).get("cost") or {}).get("spent")}
    if not o.no_pull:
        info["pulled"], left = pull_changed(o, sid, before, snapshot(sid), o.pull_max_mb)
        if left:
            info["left_in_session"] = left
    out = res.get("json") or []
    if out and isinstance(out[-1], dict):
        out[-1]["cloud"] = info
        for j in out:
            print(json.dumps(j, separators=(",", ":")))
    else:
        print(json.dumps({"ok": False, "returncode": res.get("code"), "error": res.get("error"),
                          "log_tail": res.get("tail"), "cloud": info}, separators=(",", ":")))
    ok = res.get("code") == 0 and out and not (isinstance(out[-1], dict) and out[-1].get("ok") is False)
    return 0 if ok else 1


def cmd_expr(o, st):
    sid = session(o, st)
    with tempfile.TemporaryDirectory(prefix="bas_expr_") as tmp:
        f = Path(tmp) / "args.json"
        f.write_text(json.dumps({"code": o.code}), "utf-8")
        d = start(sid, "run", ["-c", EXPR, "--args", "@" + str(f)], o.timeout)
    r = (d or {}).get("result") or {}
    if r.get("stdout"):
        print(r["stdout"].rstrip())
    if r.get("result") is not None:
        print(json.dumps(r["result"], default=str))
    if (d or {}).get("status") != "ok":
        print(json.dumps({"ok": False, "stderr": ((d or {}).get("stderr") or "")[-3000:],
                          "stdout": ((d or {}).get("stdout") or "")[-2000:]}))
        return 1
    return 0


def cmd_exec(o, st):
    """A shell command in the session's /work (ffmpeg, unzip, a separate blender -b...), followed to its end."""
    sid = session(o, st)
    if not (o.command or o.args):
        raise CloudError("exec needs a command: cloud.py exec \"ls -la\", or cloud.py exec -- prog args", 2)
    before = snapshot(sid) if not o.no_pull else {}
    d = start(sid, "exec", [o.command] if o.command else ["--", *o.args], o.timeout) or {}
    info = {"session": sid, "spent": (d.get("cost") or {}).get("spent")}
    if not o.no_pull:
        info["pulled"], left = pull_changed(o, sid, before, snapshot(sid), o.pull_max_mb)
        if left:
            info["left_in_session"] = left
    code = d.get("exit_code")
    print(json.dumps({"ok": code == 0, "exit_code": code, "stdout": (d.get("stdout") or "")[-4000:],
                      "stderr": (d.get("stderr") or "")[-2000:], "cloud": info}))
    return 0 if code == 0 else 1


def cmd_look(o, st):
    sid = session(o, st)
    out = Path(o.output)
    a = ["blender", "look", sid, "-o", str(out), "--max-size", o.max_size]
    for k in ("camera", "angles", "engine"):
        if getattr(o, k):
            a += [f"--{k}", getattr(o, k)]
    if out.suffix.lower() == ".png":
        a += ["--format", "png"]
    _, d = pch(*a, timeout=300)
    print(json.dumps({"ok": out.exists(), "file": str(out), "session": sid,
                      **{k: v for k, v in (d or {}).items() if k in ("width", "height", "views")}}))
    return 0 if out.exists() else 1


def cmd_render(o, st):
    sid = session(o, st)
    name = Path(o.blend).stem if o.blend else "scene"
    remote = f"_render/{name}-{int(time.time())}.blend"
    if o.blend and Path(o.blend).exists():          # a local file: send it, then pack in the session
        pch("blender", "open", sid, upload(o, sid, [o.blend])[o.blend], "--timeout-s", 120, timeout=600)
    elif o.blend:                                   # a /work path
        pch("blender", "open", sid, o.blend, "--timeout-s", 120, timeout=300)
    with tempfile.TemporaryDirectory(prefix="bas_render_") as tmp:
        f = Path(tmp) / "args.json"
        f.write_text(json.dumps({"path": "/work/" + remote}), "utf-8")
        _, d = pch("blender", "run", sid, "-c", PACK, "--args", "@" + str(f), "--timeout-s", 300,
                   timeout=420)
        scene = (d or {}).get("result") or {}
        pch("blender", "files", "download", sid, remote, "-o", tmp, timeout=1800)  # copies it to your files
    a = ["blender", "render", f"sessions/{sid}/{remote}", "--gpu", o.gpu, "--wait", o.timeout,
         "--name", o.name or name]
    for k in ("frames", "engine", "video", "max_cost"):
        v = getattr(o, k)
        if v:
            a += [f"--{k.replace('_', '-')}", v]
    code, job = pch(*a, ok=(0, 1, 3, 7), timeout=o.timeout + 120)
    jid = (job or {}).get("id") or (job or {}).get("job")
    while code == 7 and jid:
        code, job = pch("jobs", "wait", jid, "--wait", 600, ok=(0, 1, 3, 4, 7), timeout=720)
        if code == 7:
            continue
        _, job = pch("jobs", "status", jid, timeout=120)
    outdir = Path(o.output)
    outdir.mkdir(parents=True, exist_ok=True)
    files = []
    if jid:
        _, outs = pch("jobs", "outputs", jid, "--download", str(outdir), "--limit", 1000, ok=(0, 1),
                      timeout=3600)
        files = sorted(str(p.relative_to(outdir)) for p in outdir.rglob("*") if p.is_file())
    state = (job or {}).get("state")
    print(json.dumps({"ok": state == "succeeded", "job": jid, "state": state, "scene": scene,
                      "cost": (job or {}).get("cost"), "out": str(outdir), "files": files[:200]},
                     separators=(",", ":")))
    return 0 if state == "succeeded" else (3 if code == 3 else 1)


def cmd_push(o, st):
    sid = session(o, st)
    m = upload(o, sid, o.paths)
    print(json.dumps({"ok": True, "session": sid, "sent": m}))
    return 0


def cmd_pull(o, st):
    sid = session(o, st)
    got, refused = pull(o, sid, o.paths)
    print(json.dumps({"ok": bool(got), "session": sid, "pulled": got, "not_pulled": refused}))
    return 0 if got else 1


def cmd_fork(o, st):
    """Copies of a session as it is now (files and scene; Python's variables start fresh), to try things
    side by side. Each runs, and costs, on its own: pass --session <id> to use one, and stop each."""
    sid = session(o, st)
    a = ["blender", "session", "fork", sid, "--count", o.count, "--wait", "120"]
    if o.name:
        a += ["--name", o.name]
    _, d = pch(*a, ok=(0, 7), timeout=600)
    ids = []

    def walk(x):
        if isinstance(x, dict):
            if isinstance(x.get("id"), str) and x["id"].startswith("ses_") and x["id"] != sid:
                ids.append(x["id"])
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(d)
    ids = list(dict.fromkeys(ids))
    synced = st.setdefault("synced", {})
    for f in ids:  # a fork has its parent's files, skills included
        if sid in synced:
            synced[f] = synced[sid]
    save_state(o.dir, st)
    print(json.dumps({"ok": bool(ids), "parent": sid, "forks": ids,
                      "next": "cloud.py --session <fork> run ...; stop each with cloud.py --session <fork> stop"}))
    return 0 if ids else 1


def cmd_start(o, st):
    sid = start_session(o, st)
    sync_skills(o, sid, st)
    print(json.dumps({"ok": True, "session": sid, "watch": "https://patch.gg/blender"}))
    return 0


def cmd_status(o, st):
    sid = o.session or st.get("session")
    out = {"ok": True, "session": sid}
    if sid:
        _, s = pch("blender", "session", "view", sid, timeout=60)
        out.update({k: s.get(k) for k in ("state", "name", "size", "gpu", "blender_version", "cost")})
    _, c = pch("credits", timeout=60)
    out["credits"] = {k: (c or {}).get(k) for k in ("balance", "held", "available")}
    print(json.dumps(out))
    return 0


def cmd_stop(o, st):
    sid = o.session or st.get("session")
    if not sid:
        print(json.dumps({"ok": True, "note": "no session saved here"}))
        return 0
    _, s = pch("blender", "session", "stop", sid, timeout=120)
    st.get("synced", {}).pop(sid, None)
    if st.get("session") == sid:
        st.pop("session", None)
    if st.get("session") or st.get("synced"):
        save_state(o.dir, st)
    else:
        (o.dir / STATE).unlink(missing_ok=True)  # nothing left to remember here
    print(json.dumps({"ok": True, "session": sid, "state": (s or {}).get("state"),
                      "spent": ((s or {}).get("cost") or {}).get("spent")}))
    return 0


def parse(argv):
    rest = []
    if "--" in argv:
        i = argv.index("--")
        argv, rest = argv[:i], argv[i + 1:]
    common = argparse.ArgumentParser(add_help=False)   # accepted before or after the command
    common.add_argument("--session", default=argparse.SUPPRESS)
    common.add_argument("--dir", default=argparse.SUPPRESS, help="the folder mirrored to /work (here)")
    common.add_argument("--timeout", type=int, default=argparse.SUPPRESS, help="seconds (600)")
    common.add_argument("--name", default=argparse.SUPPRESS, help="a new session's or render's name")
    p = argparse.ArgumentParser(prog="cloud.py", description=__doc__.splitlines()[0], parents=[common])
    sp = p.add_subparsers(dest="cmd", required=True)
    add = sp.add_parser

    def sub(name):
        return add(name, parents=[common])
    sp.add_parser = sub
    r = sp.add_parser("run")
    r.add_argument("script")
    r.add_argument("--blend")
    r.add_argument("--process", action="store_true", help="a separate headless Blender, not the live scene")
    r.add_argument("--upload", action="append", help="also send this file/folder (textures a .blend needs)")
    r.add_argument("--no-pull", action="store_true")
    r.add_argument("--pull-max-mb", type=float, default=500)
    x = sp.add_parser("exec")
    x.add_argument("command", nargs="?", help="one string for bash; or put the program and its args after --")
    x.add_argument("--no-pull", action="store_true")
    x.add_argument("--pull-max-mb", type=float, default=500)
    e = sp.add_parser("expr")
    e.add_argument("code")
    lk = sp.add_parser("look")
    lk.add_argument("-o", "--output", default="look.jpg")
    lk.add_argument("--camera")
    lk.add_argument("--angles")
    lk.add_argument("--engine", choices=["workbench", "eevee"])
    lk.add_argument("--max-size", default="768")
    rd = sp.add_parser("render")
    rd.add_argument("blend", nargs="?")
    rd.add_argument("-o", "--output", default="renders")
    rd.add_argument("--frames")
    rd.add_argument("--engine", choices=["cycles", "eevee", "workbench"])
    rd.add_argument("--video", choices=["mp4", "mov"])
    rd.add_argument("--gpu", default="l40s", choices=["l40s", "l4"])
    rd.add_argument("--max-cost")
    for n in ("push", "pull"):
        sp.add_parser(n).add_argument("paths", nargs="+")
    fk = sp.add_parser("fork")
    fk.add_argument("--count", type=int, default=1)
    s = sp.add_parser("start")
    s.add_argument("--size", choices=["small", "medium", "large"])
    s.add_argument("--gpu", choices=["l4", "l40s"])
    sp.add_parser("status")
    sp.add_parser("stop")
    o = p.parse_args(argv)
    for k, v in (("session", None), ("dir", "."), ("timeout", 600), ("name", None)):
        if not hasattr(o, k):
            setattr(o, k, v)
    o.args = rest
    o.dir = Path(o.dir).resolve()
    return o


def main(argv=None):
    o = parse(sys.argv[1:] if argv is None else argv)
    st = load_state(o.dir)
    try:
        return globals()["cmd_" + o.cmd](o, st)
    except CloudError as e:
        print(json.dumps({"ok": False, "error": str(e), **({"details": e.details} if e.details else {})}))
        return e.code


if __name__ == "__main__":
    sys.exit(main())
