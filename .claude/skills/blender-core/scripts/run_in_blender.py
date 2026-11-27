#!/usr/bin/env python3
"""Run a skill script in headless Blender and print only its JSON result.

Host-side (system Python 3.9+, no bpy). Runs on Patch's cloud Blender by default once Patch's
`pch` CLI is installed (see blender-cloud); --local, or BAS_BACKEND=local, uses a Blender on this
machine instead, found automatically: $BLENDER_EXE > PATH > standard install dirs (newest wins).

Usage:
  python run_in_blender.py [--blend FILE] [--user-prefs] SCRIPT.py [-- script args]
  python run_in_blender.py --expr "import bpy; print(bpy.app.version_string)"
  python run_in_blender.py --which          # print the Blender path it would use
  python run_in_blender.py --local ...       # a Blender on this machine, not the cloud
  python run_in_blender.py [--session ses_...] [--process] ...   # cloud options: blender-cloud/scripts/cloud.py
Exit code: 0 ok, 1 script error, 2 Blender not found.
"""
import glob
import json
import os
import re
import shutil
import subprocess
import sys

MARK = "@@JSON@@"


def _ver(path):
    m = re.search(r"(\d+)\.(\d+)", path)
    return (int(m.group(1)), int(m.group(2))) if m else (0, 0)


def find_blender():
    env = os.environ.get("BLENDER_EXE")
    if env and os.path.isfile(env):
        return env
    hit = shutil.which("blender")
    if hit:
        return hit
    pats = {
        "win32": [r"C:\Program Files\Blender Foundation\Blender *\blender.exe",
                  os.path.expandvars(r"%LOCALAPPDATA%\Programs\Blender Foundation\Blender *\blender.exe"),
                  r"C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe"],
        "darwin": ["/Applications/Blender*.app/Contents/MacOS/Blender",
                   os.path.expanduser("~/Applications/Blender*.app/Contents/MacOS/Blender")],
    }.get(sys.platform, ["/usr/bin/blender", "/opt/blender*/blender", "/snap/bin/blender",
                         os.path.expanduser("~/blender*/blender")])
    found = [p for pat in pats for p in glob.glob(pat) if os.path.isfile(p)]
    return max(found, key=_ver) if found else None


def main():
    a = sys.argv[1:]
    rest = []
    if "--" in a:
        i = a.index("--")
        a, rest = a[:i], a[i + 1:]
    if backend(a) == "cloud":
        return cloud_main(a, rest)
    exe = find_blender()
    if not exe:
        print(json.dumps({"ok": False, "error": "Blender not found. Run it on Patch's cloud Blender instead, "
                          "with nothing to install: set up pch (blender-cloud skill: npm i -g @patchgg/cli, "
                          "then pch login) and call this again without --local; or set BLENDER_EXE"}))
        return 2
    if "--which" in a:
        print(exe)
        return 0
    cmd = [exe, "-b"]
    if "--blend" in a:
        cmd.append(a[a.index("--blend") + 1])
    if "--user-prefs" not in a:
        cmd.append("--factory-startup")
    cmd += ["--python-exit-code", "1"]
    if "--expr" in a:
        cmd += ["--python-expr", a[a.index("--expr") + 1]]
    else:
        scripts = [x for x in a if x.endswith(".py")]
        if not scripts:
            print(__doc__)
            return 1
        cmd += ["-P", scripts[0]]
    cmd += ["--"] + rest
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    out = [ln[len(MARK):] for ln in p.stdout.splitlines() if ln.startswith(MARK)]
    if out:
        print("\n".join(out))
    elif "--expr" in a:
        # free-form expression: show stdout minus Blender banner noise
        noise = ("Blender ", "Read prefs", "Read blend", "Blender quit", "Color management")
        print("\n".join(ln for ln in p.stdout.splitlines() if ln and not ln.startswith(noise)))
    if p.returncode != 0 and not out:
        tail = (p.stderr or p.stdout).strip().splitlines()[-15:]
        print(json.dumps({"ok": False, "returncode": p.returncode, "log_tail": tail}))
    return 0 if p.returncode == 0 else 1


def backend(a):
    """cloud (Patch's cloud Blender) unless asked for local: --local/--cloud, then BAS_BACKEND, then
    cloud whenever pch is installed. A machine without pch runs its own Blender as before."""
    if "--local" in a:
        return "local"
    if "--cloud" in a:
        return "cloud"
    env = os.environ.get("BAS_BACKEND", "").lower()
    if env in ("local", "cloud"):
        return env
    return "cloud" if os.environ.get("PCH") or shutil.which("pch") else "local"


def cloud_main(a, rest):
    """--cloud: hand the same call to blender-cloud/scripts/cloud.py (Patch's cloud Blender)."""
    import importlib.util
    here = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(here, "..", "..", "blender-cloud", "scripts", "cloud.py")
    if not os.path.isfile(path):
        print(json.dumps({"ok": False, "error": "--cloud needs the blender-cloud skill installed"}))
        return 2
    spec = importlib.util.spec_from_file_location("bas_cloud", path)
    cloud = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cloud)
    pre = ["--session", a[a.index("--session") + 1]] if "--session" in a else []
    if "--which" in a:
        return cloud.main(pre + ["status"])
    if "--expr" in a:
        return cloud.main(pre + ["expr", a[a.index("--expr") + 1]])
    scripts = [x for x in a if x.endswith(".py")]
    if not scripts:
        print(__doc__)
        return 1
    run = ["run", scripts[0]]
    if "--blend" in a:
        run += ["--blend", a[a.index("--blend") + 1]]
    if "--process" in a:
        run.append("--process")
    return cloud.main(pre + run + ["--"] + rest)


if __name__ == "__main__":
    sys.exit(main())
