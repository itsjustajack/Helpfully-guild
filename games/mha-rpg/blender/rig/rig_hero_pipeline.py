"""Rig the male base with the blender-character-rigging skill scripts (cloud/headless).

Steps: build body -> Rigify basic_human metarig -> place joints on the body's real
joints (A-pose arms) -> generate control rig -> heat-weight skin (max 4 bones)
-> stress poses -> rig_check. Needs .claude/skills/blender-character-rigging.
Run:  python -I games/mha-rpg/blender/rig/rig_hero_pipeline.py
"""
import os, sys, runpy, json, math, bpy
HERE = os.path.dirname(os.path.abspath(__file__))
from mathutils import Vector as V
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "..", ".claude", "skills",
                                "blender-character-rigging", "scripts"))
bpy.ops.wm.read_factory_settings(use_empty=True)
runpy.run_path(os.path.join(HERE, "..", "male_base.py"))
body = bpy.data.objects["SM_MaleBase"]; body.lock_location=(False,)*3; body.location=(0,0,0)
bpy.context.view_layer.update()
import rigify_build, bind_mesh, stress_poses, rig_check
print("S1", rigify_build.run(add="basic_human", fit="SM_MaleBase", no_face=True))
meta = bpy.data.objects["META_SM_MaleBase"]
for o in bpy.context.view_layer.objects: o.select_set(False)
meta.select_set(True); bpy.context.view_layer.objects.active = meta
bpy.ops.object.mode_set(mode="EDIT")
eb = meta.data.edit_bones
inv = meta.matrix_world.inverted()
A = math.radians(30)
def place(name, head, tail, mirror=True):
    for side, s in ((".L", 1), (".R", -1)) if mirror else (("", 1),):
        b = eb[name + side]
        b.head = inv @ V((head[0]*s, head[1], head[2]))
        b.tail = inv @ V((tail[0]*s, tail[1], tail[2]))
d = V((math.sin(A), 0, -math.cos(A)))
sh = V((0.215, 0.0, 1.450)); el = sh + d*0.300 + V((0, 0.012, 0)); wr = el + d*0.255
place("shoulder", (0.020, -0.030, 1.470), (0.150, 0.000, 1.462))
place("upper_arm", sh, el); place("forearm", el, wr); place("hand", wr, wr + d*0.100)
hip = V((0.088, 0.0, 0.920)); knee = V((0.096, -0.014, 0.500)); ank = V((0.098, 0.012, 0.090))
place("thigh", hip, knee); place("shin", knee, ank)
place("foot", ank, (0.100, -0.100, 0.030)); place("toe", (0.100, -0.100, 0.030), (0.102, -0.200, 0.030))
place("heel.02", (0.070, 0.050, 0.000), (0.130, 0.050, 0.000))
place("pelvis", (0.0, 0.040, 0.930), (0.110, -0.040, 1.040))
place("breast", (0.090, 0.030, 1.330), (0.090, -0.100, 1.330))
for n in ("upper_arm", "forearm", "thigh", "shin"):
    for s in (".L", ".R"):
        eb[n + s].roll = 0.0
bpy.ops.object.mode_set(mode="OBJECT")
print("S2", rigify_build.run(metarig="META_SM_MaleBase", generate=True))
print("S3", json.dumps(bind_mesh.run(armature="RIG_SM_MaleBase", meshes=["SM_MaleBase"]))[:400])
print("S4", json.dumps(stress_poses.run(armature="RIG_SM_MaleBase"))[:300])
print("S5", json.dumps(rig_check.run(armature="RIG_SM_MaleBase", meshes=["SM_MaleBase"]))[:900])
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "MaleBase_rigged.blend"))
