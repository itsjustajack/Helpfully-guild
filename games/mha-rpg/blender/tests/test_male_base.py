"""Acceptance tests for male_base.py (run with a Python that has `bpy`).

    python -I games/mha-rpg/blender/tests/test_male_base.py

Checks the body against the look Bailey asked for (stylized male mannequin):
real height, male V shape, visible soft joints, real-size feet, and the
blender-asset-qa Checker. Prints PASS/FAIL per check, exits 1 on any failure.
"""
import os
import runpy
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "..", "male_base.py")
QA_DIR = os.path.join(HERE, "..", "..", "..", "..", ".claude", "skills",
                      "blender-asset-qa", "scripts")

sys.dont_write_bytecode = True
bpy.ops.wm.read_factory_settings(use_empty=True)
runpy.run_path(SCRIPT)
body = bpy.data.objects["SM_MaleBase"]
me = body.data
BVH = BVHTree.FromPolygons([v.co.copy() for v in me.vertices],
                           [tuple(p.vertices) for p in me.polygons])
ZS = [v.co.z for v in me.vertices]


def span(origin, axis):
    """Distance between the surfaces hit when casting both ways along `axis`
    from a point INSIDE the body (true cross-section, not sparse vertices)."""
    o = Vector(origin)
    a = Vector(axis)
    hit_p = BVH.ray_cast(o, a)[0]
    hit_n = BVH.ray_cast(o, -a)[0]
    if hit_p is None or hit_n is None:
        return 0.0
    return (hit_p - hit_n).length


def width_x(z):            # torso width, cast from the spine outward
    return span((0, 0.005, z), (1, 0, 0))


def depth_y(z, x=0.097):   # leg depth, cast from the leg centre front/back
    return span((x, 0.005, z), (0, 1, 0))


results = []


def check(name, ok, detail):
    results.append(ok)
    print(f"{'PASS' if ok else 'FAIL'}  {name}: {detail}")


height = max(ZS) - min(ZS)
check("height", 1.75 <= height <= 1.85, f"{height:.3f} m (want 1.75-1.85)")

chest = width_x(1.30)      # below the armpits, so rays stay in the torso
waist = width_x(1.11)
hip = width_x(0.93)
check("male V shape", chest / hip >= 1.10,
      f"chest/hip = {chest / hip:.2f} (want >= 1.10)")
check("waist: narrow but not pinched", 1.25 <= chest / waist <= 1.50,
      f"chest/waist = {chest / waist:.2f} (want 1.25-1.50)")

knee = depth_y(0.50)
calf = depth_y(0.36)
ankle = depth_y(0.13)
check("knee reads as a joint", calf / knee >= 1.12,
      f"calf/knee depth = {calf / knee:.2f} (want >= 1.12)")
check("slim ankle", ankle / calf <= 0.65,
      f"ankle/calf depth = {ankle / calf:.2f} (want <= 0.65)")

foot = span((0.100, -0.060, 0.035), (0, 1, 0))
check("real-size foot", 0.24 <= foot <= 0.29, f"{foot:.3f} m long (want 0.24-0.29)")

sys.path.insert(0, QA_DIR)
import qa_check  # noqa: E402

qa = qa_check.run(objects=["SM_MaleBase"])
check("blender-asset-qa", bool(qa.get("pass")), f"errors={qa.get('errors')}")

print(f"\n{sum(results)}/{len(results)} checks passed")
sys.exit(0 if all(results) else 1)
