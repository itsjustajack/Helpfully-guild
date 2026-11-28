"""Anime character built on the MPFB CC0 male body (see README.md here).

Run inside Blender: Scripting tab -> New -> paste -> Run Script.
Needs mpfb_male_body.obj (made by build_body.py) in the same folder.
Base body stays bare. Separate objects on top: spiky hair, big anime eyes, brows. No clothes.
Look: 3-step cel shading + ink outline (EEVEE; set the viewport to Rendered).
Safe to re-run: it deletes only its own collection.
"""
import json
import math
import os

import bmesh
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else ""
OBJ = os.path.join(HERE, "mpfb_male_body.obj")
COL = "AnimeCharacter"

old = bpy.data.collections.get(COL)
if old:
    for ob in list(old.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    bpy.data.collections.remove(old)
col = bpy.data.collections.new(COL)
bpy.context.scene.collection.children.link(col)

# ---- the body ------------------------------------------------------------------------------
before = set(bpy.data.objects)
bpy.ops.wm.obj_import(filepath=OBJ, forward_axis="NEGATIVE_Y", up_axis="Z")
body = next(o for o in bpy.data.objects if o not in before)
for c in list(body.users_collection):
    c.objects.unlink(body)
col.objects.link(body)
body.name = body.data.name = "SM_Anime_Body"
base = body.data
_bm = bmesh.new()
_bm.from_mesh(base)
bmesh.ops.recalc_face_normals(_bm, faces=_bm.faces)     # every face pointing OUT (clothes are offset along these)
_bm.to_mesh(base)
_bm.free()
base.shade_smooth()
# anime face: fill the eye sockets / flatten brow and cheek around the eyes so big eyes sit on a flat plane
_eyes = json.load(open(os.path.join(HERE, "eye_positions.json")))
EZ = _eyes["helper-l-eye"][2]
EX = abs(_eyes["helper-l-eye"][0])
FACE_Y = -0.0475
for v in base.vertices:
    co = v.co
    dx = (abs(co.x) - EX * 1.05) / 0.040
    dz = (co.z - EZ) / 0.052
    r2 = dx * dx + dz * dz
    if r2 < 1.0 and co.y > FACE_Y:
        w = (1.0 - r2) ** 1.2
        co.y += (FACE_Y - co.y) * min(1.0, w * 1.15)
base.update()
bvh = BVHTree.FromPolygons([v.co.copy() for v in base.vertices], [tuple(p.vertices) for p in base.polygons])

PAL = {
    "skin": (0.88, 0.64, 0.50), "shirt": (0.78, 0.10, 0.12), "jeans": (0.07, 0.09, 0.17),
    "shoe": (0.92, 0.92, 0.95), "sole": (0.14, 0.14, 0.17), "hair": (0.06, 0.08, 0.20),
    "eye_white": (0.97, 0.97, 1.0), "iris": (0.10, 0.60, 0.95), "pupil": (0.02, 0.03, 0.08),
    "shine": (1.0, 1.0, 1.0), "brow": (0.04, 0.05, 0.12), "belt": (0.10, 0.06, 0.04),
}
MATS = {}


def mat(key, rough=0.7):
    if key in MATS:
        return MATS[key]
    name = "M_Anime_" + key.title().replace("_", "")
    m = bpy.data.materials.get(name)
    if m:
        bpy.data.materials.remove(m)
    m = bpy.data.materials.new(name)
    if not m.node_tree:
        m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*PAL[key], 1)
    b.inputs["Roughness"].default_value = rough
    m["base"] = list(PAL[key])
    MATS[key] = m
    return m


base.materials.clear()
base.materials.append(mat("skin", 0.55))


def garment(name, region, cuts, off, thick, key, rough=0.8):
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
    s = ob.modifiers.new("Thickness", "SOLIDIFY")
    s.thickness = thick
    s.offset = 1.0
    s.use_even_offset = False       # 'even' blows up on thin boot geometry
    me.shade_smooth()
    return ob


def shape(name, kind, loc, size, key, rot=(0, 0, 0), rough=0.5):
    b = bmesh.new()
    if kind == "ball":
        bmesh.ops.create_uvsphere(b, u_segments=24, v_segments=14, radius=1.0, matrix=Matrix.Diagonal((*size, 1.0)))
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


UP, DOWN = Vector((0, 0, 1)), Vector((0, 0, -1))
verts_w = [v.co for v in base.vertices]
head = [v for v in verts_w if v.z > 1.58]
zt = max(v.z for v in head)
hcx = (max(v.x for v in head) + min(v.x for v in head)) / 2
hcy = (max(v.y for v in head) + min(v.y for v in head)) / 2
hhx = (max(v.x for v in head) - min(v.x for v in head)) / 2
hhy = (max(v.y for v in head) - min(v.y for v in head)) / 2
print(f"head: top {zt:.3f}, half-width {hhx:.3f}, half-depth {hhy:.3f}, centre ({hcx:.3f}, {hcy:.3f})")

# shoulder and arm direction (right arm), measured from the mesh
arm_pts = [v for v in verts_w if v.x > 0.30 and 0.85 < v.z < 1.30]
hand = max(arm_pts, key=lambda v: v.x)
SH = Vector((0.20, 0.0, 1.43))
ARM = (hand - SH).normalized()
ARM_R, ARM_L = ARM, Vector((-ARM.x, ARM.y, ARM.z))
SH_R, SH_L = SH, Vector((-SH.x, SH.y, SH.z))

# (no clothes: Bailey wants just the character mesh in the anime style)

# ---- anime eyes (big, on the face surface), brows --------------------------------------------------------
ez, ex = EZ, EX


def on_face(x, z):
    loc, nrm, _, _ = bvh.ray_cast(Vector((x, -1.0, z)), Vector((0, 1, 0)))
    return (loc, nrm.normalized()) if loc is not None else (Vector((x, -hhy, z)), Vector((0, -1, 0)))


for sx, nm in ((1, "R"), (-1, "L")):
    p, n = on_face(sx * ex * 1.05, ez)
    q = p + n * 0.003
    white = shape(f"SM_Anime_EyeWhite{nm}", "ball", q, (0.0185, 0.0035, 0.0235), "eye_white", rough=0.2)
    iris = shape(f"SM_Anime_Iris{nm}", "ball", q + n * 0.0028, (0.0135, 0.0030, 0.0200), "iris", rough=0.2)
    shape(f"SM_Anime_Pupil{nm}", "ball", q + n * 0.0048, (0.0070, 0.0020, 0.0125), "pupil", rough=0.2)
    shape(f"SM_Anime_Shine{nm}", "ball", q + n * 0.0066 + Vector((sx * -0.004, 0, 0.007)), (0.0042, 0.0016, 0.0050), "shine", rough=0.1)
    pb, nb = on_face(sx * ex * 1.05, ez + 0.036)
    shape(f"SM_Anime_Brow{nm}", "cube", pb + nb * 0.004, (0.034, 0.006, 0.0075), "brow",
          rot=(0, sx * -0.18, 0))

# ---- anime hair: scalp cap that hugs the skull + swept, tapered locks (groomed, not a crown of cones) ----
def scalp(c):
    front = c.y < hcy - 0.03
    side = abs(c.x) > 0.055
    thr = zt - (0.070 if front else (0.095 if side else 0.17))
    return c.z > thr and c.y > FACE_Y - 0.02


garment("SM_Anime_HairCap", scalp, [], 0.010, 0.012, "hair", 0.5)


def lock(name, p0, p1, p2, r0, r1, n=8, seg=8):
    """Tapered curved lock along a quadratic curve p0 -> p1 -> p2 (a hair clump)."""
    p0, p1, p2 = Vector(p0), Vector(p1), Vector(p2)
    bm = bmesh.new()
    rings = []
    for i in range(n + 1):
        t = i / n
        pos = (1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t * t * p2
        tan = (2 * (1 - t) * (p1 - p0) + 2 * t * (p2 - p1)).normalized()
        ref = Vector((0, 0, 1)) if abs(tan.z) < 0.9 else Vector((1, 0, 0))
        a = tan.cross(ref).normalized()
        b = tan.cross(a).normalized()
        r = r0 + (r1 - r0) * (t ** 0.8)
        ring = [bm.verts.new(pos + (a * math.cos(k * math.tau / seg) + b * math.sin(k * math.tau / seg)) * r)
                for k in range(seg)]
        rings.append(ring)
    for i in range(n):
        for k in range(seg):
            bm.faces.new((rings[i][k], rings[i][(k + 1) % seg], rings[i + 1][(k + 1) % seg], rings[i + 1][k]))
    bm.faces.new(rings[0])
    bm.faces.new(list(reversed(rings[-1])))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    col.objects.link(ob)
    ob.data.materials.append(mat("hair", 0.5))
    me.shade_smooth()
    return ob


top = zt + 0.004
front_y = hcy - hhy * 0.80
# top locks: swept back and up from the crown
for i, x in enumerate((-0.06, -0.03, 0.0, 0.03, 0.06)):
    lock(f"SM_Anime_LockTop{i + 1}", (x, hcy - 0.035, top - 0.012), (x * 1.5, hcy + 0.01, top + 0.075),
         (x * 2.2, hcy + 0.10, top + 0.035), 0.017, 0.002)
# fringe: locks falling over the forehead, tips staying ABOVE the eyes
for i, x in enumerate((-0.072, -0.046, -0.018, 0.012, 0.040, 0.066)):
    lock(f"SM_Anime_LockFringe{i + 1}", (x * 0.8, front_y + 0.012, top - 0.040),
         (x * 1.1, front_y - 0.026, top - 0.022), (x * 1.6 + (0.012 if x > 0 else -0.012), front_y - 0.030, top - 0.058),
         0.018, 0.0015)
# side locks in front of the ears
for sx in (1, -1):
    for k, dy in enumerate((-0.012, 0.012)):
        lock(f"SM_Anime_LockSide{'R' if sx > 0 else 'L'}{k + 1}", (sx * 0.083, hcy - 0.03 + dy, top - 0.075),
             (sx * 0.098, hcy - 0.035 + dy, top - 0.125), (sx * 0.092, hcy - 0.025 + dy, top - 0.178), 0.016, 0.0015)
# back locks down the nape
for i, x in enumerate((-0.05, 0.0, 0.05)):
    lock(f"SM_Anime_LockBack{i + 1}", (x, hcy + hhy * 0.55, top - 0.09), (x * 1.2, hcy + hhy * 0.95, top - 0.14),
         (x * 1.1, hcy + hhy * 0.80, top - 0.215), 0.022, 0.003)

# ---- cel shading + ink outline --------------------------------------------------------------------------------
ink = bpy.data.materials.get("M_Anime_Ink") or bpy.data.materials.new("M_Anime_Ink")
if not ink.node_tree:
    ink.use_nodes = True
ink.node_tree.nodes.clear()
o_ = ink.node_tree.nodes.new("ShaderNodeOutputMaterial")
e_ = ink.node_tree.nodes.new("ShaderNodeEmission")
e_.inputs["Color"].default_value = (0.01, 0.01, 0.025, 1)
ink.node_tree.links.new(e_.outputs["Emission"], o_.inputs["Surface"])
ink.use_backface_culling = True
NO_OUTLINE = ("Pupil", "Shine", "Iris", "Brow")
for ob in list(col.objects):
    if ob.type != "MESH" or not ob.data.materials:
        continue
    m0 = ob.data.materials[0]
    c = list(m0.get("base", PAL["skin"]))
    t = bpy.data.materials.new(m0.name + "_Toon")
    t.use_nodes = True
    nt = t.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    dif = nt.nodes.new("ShaderNodeBsdfDiffuse")
    s2r = nt.nodes.new("ShaderNodeShaderToRGB")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    em = nt.nodes.new("ShaderNodeEmission")
    cr = ramp.color_ramp
    cr.interpolation = "CONSTANT"
    cr.elements[0].position = 0.0
    cr.elements[0].color = (c[0] * 0.55, c[1] * 0.50, c[2] * 0.62, 1)
    cr.elements[1].position = 0.30
    cr.elements[1].color = (*c, 1)
    hi = cr.elements.new(0.84)
    hi.color = (min(c[0] * 1.15 + 0.03, 1), min(c[1] * 1.15 + 0.03, 1), min(c[2] * 1.12 + 0.04, 1), 1)
    nt.links.new(dif.outputs["BSDF"], s2r.inputs["Shader"])
    nt.links.new(s2r.outputs["Color"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], em.inputs["Color"])
    nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
    ob.data.materials.clear()
    ob.data.materials.append(t)
    ob.data.materials.append(ink)
    for p in ob.data.polygons:
        p.material_index = 0
    if not any(k in ob.name for k in NO_OUTLINE):
        so = ob.modifiers.new("InkOutline", "SOLIDIFY")
        so.thickness = 0.0035 if "Eye" not in ob.name else 0.0012
        so.offset = 1.0
        so.use_flip_normals = True
        so.use_rim = False
        so.material_offset = 1
print(f"Anime character built: {len(col.objects)} objects")
