"""Build a male body mesh from MPFB's CC0 base mesh + shape adjustments ("targets"). Plain Python.

    python3 -I games/characters/mpfb/build_body.py [muscle 0..1] [height_m]
Writes mpfb_male_body.obj next to this file: body only (helper geometry removed), in Blender
coordinates (Z up, faces -Y), in metres, feet on the floor, with UVs.
"""
import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "data")
MUSCLE = float(sys.argv[1]) if len(sys.argv) > 1 else 0.55
HEIGHT = float(sys.argv[2]) if len(sys.argv) > 2 else 1.78
BODY_VERTS = 13380                  # vertices 0..13379 are the body; the rest is helper geometry

verts, uvs, faces = [], [], []
for line in open(os.path.join(D, "base.obj")):
    p = line.split()
    if not p:
        continue
    if p[0] == "v":
        verts.append([float(p[1]), float(p[2]), float(p[3])])
    elif p[0] == "vt":
        uvs.append((float(p[1]), float(p[2])))
    elif p[0] == "f":
        faces.append([tuple(int(i) if i else 0 for i in tok.split("/")[:2]) for tok in p[1:]])


def target(name):
    out = {}
    raw = gzip.decompress(open(os.path.join(D, name + ".target.gz"), "rb").read()).decode()
    for line in raw.splitlines():
        t = line.split()
        if len(t) == 4 and not line.startswith("#"):
            out[int(t[0])] = (float(t[1]), float(t[2]), float(t[3]))
    return out


def apply(name, weight):
    for i, (dx, dy, dz) in target(name).items():
        verts[i][0] += dx * weight
        verts[i][1] += dy * weight
        verts[i][2] += dz * weight


apply("caucasian-male-young", 0.5)           # male, young adult (blend of two ethnic base shapes)
apply("asian-male-young", 0.5)
apply("universal-male-young-maxmuscle-averageweight", MUSCLE)       # more muscle
apply("male-young-averagemuscle-averageweight-idealproportions", 1.0)  # heroic proportions

body = verts[:BODY_VERTS]
miny = min(v[1] for v in body)
maxy = max(v[1] for v in body)
scale = HEIGHT / (maxy - miny)
out = os.path.join(HERE, "mpfb_male_body.obj")
with open(out, "w") as f:
    f.write("# MPFB CC0 base mesh, male body only\n")
    for x, y, z in body:           # MakeHuman: Y up, Z toward viewer. Written as Blender coords: Z up, -Y = front
        f.write(f"v {x * scale:.5f} {z * scale:.5f} {(y - miny) * scale:.5f}\n")   # (flip checked with the nose tip)
    for u, v in uvs:
        f.write(f"vt {u:.5f} {v:.5f}\n")
    kept = 0
    for fc in faces:
        if all(0 < vi <= BODY_VERTS for vi, _ in fc):
            f.write("f " + " ".join(f"{vi}/{ti}" for vi, ti in fc) + "\n")
            kept += 1
print(f"wrote {out}: {BODY_VERTS} verts, {kept} faces, height {HEIGHT} m, muscle {MUSCLE}")

# eye positions for the anime eyes (helper-l-eye / helper-r-eye groups), same coordinates (nose tip check below)
groups = json.load(open(os.path.join(D, "basemesh_vertex_groups.json")))
eyes = {}
for key in ("helper-l-eye", "helper-r-eye"):
    idx = []
    for a, b in groups[key]:
        idx += list(range(a, b + 1))
    pts = [verts[i] for i in idx]
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    cz = sum(p[2] for p in pts) / len(pts)
    eyes[key] = [cx * scale, cz * scale, (cy - miny) * scale]
json.dump(eyes, open(os.path.join(HERE, "eye_positions.json"), "w"))
print("eyes:", eyes)

# sanity: the nose tip (most forward head vertex) must end up at the most negative Y (front = -Y)
head = [i for i in range(BODY_VERTS) if verts[i][1] > (miny + (maxy - miny) * 0.9)]
nose = max(head, key=lambda i: verts[i][2])
print("nose tip y in file:", round(verts[nose][2] * scale, 3), "(should be the head's most negative-Y point after import)")
