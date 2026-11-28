"""Test character in normal clothing (t-shirt, jeans, sneakers) on the locked base body.

Run inside Blender: Scripting tab -> New -> paste -> Run Script.
Needs games/mha-rpg/blender/male_base.py (run first to make the body).
Base body stays bald and bare; every piece of clothing is a SEPARATE object on top.
Safe to re-run: it deletes only its own collection.
"""
import math
import os
import runpy

import bmesh
import bpy
from mathutils import Matrix, Vector

COL = "NormalCharacter"
HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else ""
BODY_SCRIPT = os.path.normpath(os.path.join(HERE, "..", "mha-rpg", "blender", "male_base.py"))

old = bpy.data.collections.get(COL)
if old:
    for ob in list(old.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    bpy.data.collections.remove(old)

runpy.run_path(BODY_SCRIPT)
body = bpy.data.objects["SM_MaleBase"]
body.lock_location = (False, False, False)
body.location = (0, 0, 0)
body.name = body.data.name = "SM_Normal_Body"
mc = bpy.data.collections.get("MaleBase")
col = bpy.data.collections.new(COL)
bpy.context.scene.collection.children.link(col)
col.objects.link(body)
mc.objects.unlink(body)
for o in list(mc.objects):
    bpy.data.objects.remove(o, do_unlink=True)
bpy.data.collections.remove(mc)
base = body.data

PAL = {
    "skin": (0.74, 0.52, 0.40), "shirt": (0.55, 0.57, 0.60), "jeans": (0.10, 0.17, 0.32),
    "shoe": (0.86, 0.86, 0.88), "sole": (0.60, 0.50, 0.30), "hair": (0.04, 0.03, 0.03),
    "eye": (0.03, 0.02, 0.02), "belt": (0.15, 0.09, 0.05), "lip": (0.50, 0.28, 0.25),
}


def mat(key, rough=0.7):
    name = "M_Normal_" + key.title()
    m = bpy.data.materials.get(name)
    if m:
        bpy.data.materials.remove(m)
    m = bpy.data.materials.new(name)
    if not m.node_tree:
        m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*PAL[key], 1)
    b.inputs["Roughness"].default_value = rough
    return m


body.data.materials.clear()
body.data.materials.append(mat("skin", 0.55))


def garment(name, region, cuts, off, thick, key, rough=0.8):
    """Body faces inside `region` (coarse), trimmed with straight plane cuts, pushed out, thickened.
    cuts: list of (point, normal): everything on the +normal side of the plane is discarded."""
    bm = bmesh.new()
    bm.from_mesh(base)
    drop = [f for f in bm.faces if not region(f.calc_center_median())]
    bmesh.ops.delete(bm, geom=drop, context="FACES")
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    for co, no in cuts:
        geom = list(bm.verts) + list(bm.edges) + list(bm.faces)
        bmesh.ops.bisect_plane(bm, geom=geom, plane_co=co, plane_no=no, clear_outer=True)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    bm.normal_update()
    for v in bm.verts:
        v.co += v.normal * off
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    col.objects.link(ob)
    ob.data.materials.append(mat(key, rough))
    s_ = ob.modifiers.new("Thickness", "SOLIDIFY")
    s_.thickness = thick
    s_.offset = 1.0
    s_.use_even_offset = True
    me.shade_smooth()
    return ob


def shape(name, kind, loc, size, key, rot=(0, 0, 0), rough=0.6):
    b = bmesh.new()
    if kind == "ball":
        bmesh.ops.create_uvsphere(b, u_segments=18, v_segments=10, radius=1.0, matrix=Matrix.Diagonal((*size, 1.0)))
    elif kind == "cone":
        bmesh.ops.create_cone(b, cap_ends=True, segments=14, radius1=size[0], radius2=size[1], depth=size[2])
    else:
        bmesh.ops.create_cube(b, size=1.0, matrix=Matrix.Diagonal((*size, 1.0)))
    me = bpy.data.meshes.new(name)
    b.to_mesh(me)
    b.free()
    ob = bpy.data.objects.new(name, me)
    ob.location = loc
    ob.rotation_euler = rot
    col.objects.link(ob)
    ob.data.materials.append(mat(key, rough))
    if kind != "cube":
        me.shade_smooth()
    return ob


# clothing: coarse region + exact plane cuts (clean hems)
UP, DOWN = Vector((0, 0, 1)), Vector((0, 0, -1))
A = math.radians(30)
ARM_R = Vector((math.sin(A), 0, -math.cos(A)))      # along the right arm, shoulder -> hand
ARM_L = Vector((-math.sin(A), 0, -math.cos(A)))
SH_R, SH_L = Vector((0.215, 0, 1.452)), Vector((-0.215, 0, 1.452))
garment("SM_Normal_Jeans", lambda c: abs(c.x) < 0.24 and 0.05 < c.z < 1.08,
        [(Vector((0, 0, 1.0)), UP), (Vector((0, 0, 0.13)), DOWN)], 0.008, 0.010, "jeans", 0.85)
garment("SM_Normal_TShirt", lambda c: 0.88 < c.z < 1.56,
        [(Vector((0, 0, 0.955)), DOWN), (Vector((0, 0, 1.505)), UP),
         (SH_R + ARM_R * 0.115, ARM_R), (SH_L + ARM_L * 0.115, ARM_L)], 0.014, 0.008, "shirt", 0.9)
garment("SM_Normal_Belt", lambda c: abs(c.x) < 0.24 and 0.90 < c.z < 1.10,
        [(Vector((0, 0, 1.005)), UP), (Vector((0, 0, 0.965)), DOWN)], 0.020, 0.012, "belt", 0.5)
garment("SM_Normal_Sneakers", lambda c: abs(c.x) < 0.24 and c.z < 0.20,
        [(Vector((0, 0, 0.125)), UP)], 0.012, 0.010, "shoe", 0.6)
garment("SM_Normal_Soles", lambda c: abs(c.x) < 0.24 and c.z < 0.10,
        [(Vector((0, 0, 0.032)), UP)], 0.018, 0.012, "sole", 0.8)

# short hair: cap + sides + a fringe
shape("SM_Normal_Hair", "ball", (0, 0.014, 1.752), (0.103, 0.112, 0.082), "hair", rough=0.5)
shape("SM_Normal_HairBack", "ball", (0, 0.045, 1.700), (0.094, 0.075, 0.075), "hair", rough=0.5)
shape("SM_Normal_Fringe", "ball", (0, -0.060, 1.775), (0.090, 0.035, 0.030), "hair", rough=0.5)
# simple face: eyes, brows, nose, mouth, ears
for s_, nm in ((1, "R"), (-1, "L")):
    shape(f"SM_Normal_Eye{nm}", "ball", (s_ * 0.034, -0.0975, 1.702), (0.0125, 0.008, 0.0105), "eye", rough=0.3)
    shape(f"SM_Normal_Brow{nm}", "cube", (s_ * 0.034, -0.1000, 1.727), (0.030, 0.006, 0.006), "hair", rot=(0, 0.0, s_ * -0.12))
    shape(f"SM_Normal_Ear{nm}", "ball", (s_ * 0.090, 0.002, 1.690), (0.011, 0.020, 0.030), "skin")
shape("SM_Normal_Nose", "ball", (0, -0.106, 1.678), (0.014, 0.014, 0.020), "skin")
shape("SM_Normal_Mouth", "cube", (0, -0.0925, 1.642), (0.034, 0.006, 0.0065), "lip", rough=0.5)

tris = 0
dg = bpy.context.evaluated_depsgraph_get()
for ob in col.objects:
    ev = ob.evaluated_get(dg)
    m = ev.to_mesh()
    m.calc_loop_triangles()
    tris += len(m.loop_triangles)
    ev.to_mesh_clear()
print(f"Normal character built: {len(col.objects)} objects, {tris} tris")
