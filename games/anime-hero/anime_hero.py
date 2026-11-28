"""Anime superhero (original design) built on the male base body. For the Unity project.

Run inside Blender: Scripting tab -> New -> paste -> Run Script. (Needs the repo's
games/mha-rpg/blender/male_base.py next to it; it is run first to make the body.)

Costume = separate pieces over the locked bald base body:
  navy bodysuit, orange chest plate and belt, white gloves and boots with orange
  trim, a dark visor with a cyan glow strip, spiky silver hair, a short orange cape.
Pieces use plain colour materials (what Unity imports). For the anime look in
Blender, set TOON=True before running (adds a 3-step cel shader + ink outline).
Safe to re-run: it deletes only its own collection.
"""
import math
import os

import bmesh
import bpy
from mathutils import Matrix, Vector

TOON = globals().get("TOON", False)
COL = "AnimeHero"
HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else ""
BODY_SCRIPT = os.path.normpath(os.path.join(HERE, "..", "mha-rpg", "blender", "male_base.py"))

# ---- clean own earlier run ----------------------------------------------------------
old = bpy.data.collections.get(COL)
if old:
    for ob in list(old.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    bpy.data.collections.remove(old)

# ---- the body (from the repo's male_base.py), moved to the origin ----------------------
import runpy
runpy.run_path(BODY_SCRIPT)
body = bpy.data.objects["SM_MaleBase"]
body.lock_location = (False, False, False)
body.location = (0, 0, 0)
body.name = "SM_AnimeHero_Body"
body.data.name = "SM_AnimeHero_Body"
mc = bpy.data.collections.get("MaleBase")
col = bpy.data.collections.new(COL)
bpy.context.scene.collection.children.link(col)
col.objects.link(body)
mc.objects.unlink(body)
for o in list(mc.objects):
    bpy.data.objects.remove(o, do_unlink=True)
bpy.data.collections.remove(mc)
base = body.data

# ---- palette (flat colours, exported to Unity as material colours) -----------------------
PAL = {
    "skin": (0.80, 0.58, 0.46),
    "suit": (0.04, 0.07, 0.20),
    "orange": (0.90, 0.32, 0.06),
    "white": (0.88, 0.90, 0.94),
    "gold": (0.95, 0.70, 0.20),
    "visor": (0.03, 0.04, 0.09),
    "glow": (0.20, 0.90, 1.00),
    "hair": (0.82, 0.86, 0.95),
    "boot_trim": (0.90, 0.32, 0.06),
}
MATS = {}


def mat(key, rough=0.7, emit=False):
    if key in MATS:
        return MATS[key]
    name = "M_AnimeHero_" + key.title().replace("_", "")
    m = bpy.data.materials.get(name)
    if m:
        bpy.data.materials.remove(m)
    m = bpy.data.materials.new(name)
    if not m.node_tree:
        m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*PAL[key], 1)
    b.inputs["Roughness"].default_value = rough
    if emit:
        b.inputs["Emission Color"].default_value = (*PAL[key], 1)
        b.inputs["Emission Strength"].default_value = 4.0
    m["base"] = list(PAL[key])
    MATS[key] = m
    return m


body.data.materials.clear()
body.data.materials.append(mat("skin", 0.55))


def garment(name, cond, off, thick, key, rough=0.7):
    """Copy of the body faces that pass `cond(centroid)`, pushed out by `off`, then thickened."""
    bm = bmesh.new()
    bm.from_mesh(base)
    bm.normal_update()
    drop = [f for f in bm.faces if not cond(f.calc_center_median())]
    bmesh.ops.delete(bm, geom=drop, context="FACES")
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    for v in bm.verts:
        v.co += v.normal * off
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    col.objects.link(ob)
    ob.data.materials.append(mat(key, rough))
    s = ob.modifiers.new("Thickness", "SOLIDIFY")
    s.thickness = thick
    s.offset = 1.0
    s.use_even_offset = True
    me.shade_smooth()
    return ob


def shape(name, kind, loc, size, key, rot=(0, 0, 0), emit=False, rough=0.6):
    b = bmesh.new()
    if kind == "ball":
        bmesh.ops.create_uvsphere(b, u_segments=20, v_segments=12, radius=1.0,
                                  matrix=Matrix.Diagonal((*size, 1.0)))
    elif kind == "cone":
        bmesh.ops.create_cone(b, cap_ends=True, segments=16, radius1=size[0], radius2=size[1], depth=size[2])
    elif kind == "cube":
        bmesh.ops.create_cube(b, size=1.0, matrix=Matrix.Diagonal((*size, 1.0)))
    me = bpy.data.meshes.new(name)
    b.to_mesh(me)
    b.free()
    ob = bpy.data.objects.new(name, me)
    ob.location = loc
    ob.rotation_euler = rot
    col.objects.link(ob)
    ob.data.materials.append(mat(key, rough, emit))
    if kind != "cube":
        me.shade_smooth()
    return ob


# ---- zones of the body (A-pose, 1.79 m, faces -Y) --------------------------------------------
def hand(c):  return abs(c.x) > 0.3 and c.z < 1.03
def sleeve(c): return abs(c.x) > 0.19 and 1.03 <= c.z < 1.50
def torso(c): return abs(c.x) <= 0.19 and 0.93 < c.z < 1.50
def legs(c):  return 0.30 <= c.z <= 0.93 and abs(c.x) < 0.22
def boots(c): return c.z < 0.30 and abs(c.x) < 0.22


garment("SM_AnimeHero_Suit", lambda c: torso(c) or sleeve(c) or legs(c), 0.006, 0.008, "suit", 0.5)
garment("SM_AnimeHero_Gloves", hand, 0.010, 0.010, "white", 0.55)
garment("SM_AnimeHero_Boots", boots, 0.010, 0.012, "white", 0.55)
garment("SM_AnimeHero_BootTrim", lambda c: 0.27 < c.z < 0.31 and abs(c.x) < 0.22, 0.014, 0.008, "boot_trim", 0.5)
garment("SM_AnimeHero_ChestPlate", lambda c: abs(c.x) < 0.17 and 1.16 < c.z < 1.43 and c.y < 0.0,
        0.020, 0.012, "orange", 0.4)
garment("SM_AnimeHero_CuffL", lambda c: c.x < -0.30 and 1.03 <= c.z < 1.10, 0.016, 0.008, "orange", 0.5)
garment("SM_AnimeHero_CuffR", lambda c: c.x > 0.30 and 1.03 <= c.z < 1.10, 0.016, 0.008, "orange", 0.5)
garment("SM_AnimeHero_Belt", lambda c: abs(c.x) < 0.19 and 0.93 < c.z < 1.00, 0.020, 0.012, "gold", 0.35)

# visor + glow strip (over the eyes), hair, cape
shape("SM_AnimeHero_Visor", "ball", (0, -0.052, 1.705), (0.094, 0.062, 0.036), "visor", rough=0.25)
shape("SM_AnimeHero_VisorGlow", "ball", (0, -0.104, 1.707), (0.07, 0.012, 0.010), "glow", emit=True)
shape("SM_AnimeHero_HairBase", "ball", (0, 0.010, 1.752), (0.102, 0.108, 0.080), "hair", rough=0.5)
# spikes: (angle around the head, tilt back, length)
spikes = [(0.0, 0.55, 0.20), (0.9, 0.5, 0.18), (1.9, 0.6, 0.22), (2.8, 0.55, 0.20), (3.7, 0.5, 0.18),
          (4.6, 0.6, 0.20), (5.5, 0.5, 0.17), (0.45, 0.9, 0.15), (3.3, 0.9, 0.16)]
for i, (a, tilt, ln) in enumerate(spikes):
    cx, cy = 0.07 * math.cos(a), 0.07 * math.sin(a)
    direction = Vector((math.cos(a) * math.sin(tilt) * 0.9, math.sin(a) * math.sin(tilt) * 0.9 + 0.45, math.cos(tilt)))
    direction.normalize()
    rot = Vector((0, 0, 1)).rotation_difference(direction).to_euler()
    pos = Vector((cx, cy + 0.01, 1.77)) + direction * ln / 2
    shape(f"SM_AnimeHero_HairSpike{i + 1:02d}", "cone", pos, (0.032, 0.002, ln), "hair", rot=rot, rough=0.5)
# front fringe: three short spikes pointing forward-down over the forehead
for i, x in enumerate((-0.05, 0.0, 0.05)):
    d = Vector((x * 1.5, -0.7, -0.5)).normalized()
    rot = Vector((0, 0, 1)).rotation_difference(d).to_euler()
    shape(f"SM_AnimeHero_Fringe{i + 1}", "cone", Vector((x, -0.085, 1.775)) + d * 0.045, (0.026, 0.002, 0.10),
          "hair", rot=rot, rough=0.5)

# short cape: half a flared cone behind the shoulders (front half removed)
b = bmesh.new()
bmesh.ops.create_cone(b, cap_ends=False, segments=24, radius1=0.30, radius2=0.14, depth=0.62)
b.faces.ensure_lookup_table()
bmesh.ops.delete(b, geom=[f for f in b.faces if f.calc_center_median().y < 0.02], context="FACES")
bmesh.ops.delete(b, geom=[v for v in b.verts if not v.link_faces], context="VERTS")
me = bpy.data.meshes.new("SM_AnimeHero_Cape")
b.to_mesh(me)
b.free()
cape = bpy.data.objects.new("SM_AnimeHero_Cape", me)
cape.location = (0, 0.085, 1.17)
cape.scale = (1.0, 0.55, 1.0)
col.objects.link(cape)
cape.data.materials.append(mat("orange", 0.8))
cs = cape.modifiers.new("Thickness", "SOLIDIFY")
cs.thickness = 0.01
cs.offset = 0.0
me.shade_smooth()

# ---- optional anime look for Blender (cel shader + ink outline) ------------------------------------
if TOON:
    ink = bpy.data.materials.get("M_AnimeHero_Ink") or bpy.data.materials.new("M_AnimeHero_Ink")
    if not ink.node_tree:
        ink.use_nodes = True
    ink.node_tree.nodes.clear()
    o = ink.node_tree.nodes.new("ShaderNodeOutputMaterial")
    e = ink.node_tree.nodes.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = (0.01, 0.01, 0.02, 1)
    ink.node_tree.links.new(e.outputs["Emission"], o.inputs["Surface"])
    ink.use_backface_culling = True
    for ob in list(col.objects):
        if ob.type != "MESH" or not ob.data.materials:
            continue
        m0 = ob.data.materials[0]
        c = list(m0.get("base", PAL["suit"]))
        glow = "Glow" in m0.name
        t = bpy.data.materials.new(m0.name + "_Toon")
        t.use_nodes = True
        nt = t.node_tree
        nt.nodes.clear()
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        if glow:
            em = nt.nodes.new("ShaderNodeEmission")
            em.inputs["Color"].default_value = (*c, 1)
            em.inputs["Strength"].default_value = 3.0
            nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
        else:
            dif = nt.nodes.new("ShaderNodeBsdfDiffuse")
            s2r = nt.nodes.new("ShaderNodeShaderToRGB")
            ramp = nt.nodes.new("ShaderNodeValToRGB")
            em = nt.nodes.new("ShaderNodeEmission")
            cr = ramp.color_ramp
            cr.interpolation = "CONSTANT"
            cr.elements[0].position = 0.0
            cr.elements[0].color = (c[0] * 0.40, c[1] * 0.40, c[2] * 0.48, 1)
            cr.elements[1].position = 0.32
            cr.elements[1].color = (*c, 1)
            hi = cr.elements.new(0.82)
            hi.color = (min(c[0] * 1.35 + 0.04, 1), min(c[1] * 1.35 + 0.04, 1), min(c[2] * 1.3 + 0.05, 1), 1)
            nt.links.new(dif.outputs["BSDF"], s2r.inputs["Shader"])
            nt.links.new(s2r.outputs["Color"], ramp.inputs["Fac"])
            nt.links.new(ramp.outputs["Color"], em.inputs["Color"])
            nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
        ob.data.materials.clear()
        ob.data.materials.append(t)
        ob.data.materials.append(ink)
        for p in ob.data.polygons:
            p.material_index = 0
        if not glow:
            so = ob.modifiers.new("InkOutline", "SOLIDIFY")
            so.thickness = 0.0035
            so.offset = 1.0
            so.use_flip_normals = True
            so.use_rim = False
            so.material_offset = 1

tris = 0
dg = bpy.context.evaluated_depsgraph_get()
for ob in col.objects:
    if ob.type == "MESH":
        ev = ob.evaluated_get(dg)
        m = ev.to_mesh()
        m.calc_loop_triangles()
        tris += len(m.loop_triangles)
        ev.to_mesh_clear()
print(f"Anime hero built: {len(col.objects)} objects, {tris} tris, toon={TOON}")
