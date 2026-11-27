"""Male base mesh v4 (stylized mannequin) for the MHA RPG.

Run inside Blender: Scripting tab -> New -> paste -> Run Script.
Real-world scale (1 unit = 1 m), 1.80 m tall, faces -Y, A-pose so clothes and
rigging are easy later. Bald, faceless, no clothing: this is the BASE BODY
layer. Clothing is built as separate objects on top, later.

Built from a skeleton of points with radii, turned into a smooth body by the
Skin + Subdivision modifiers. That gives clean quad topology with no stacked
blobs or ridges. It is placed 0.6 m to the side (+X) so it does not overlap the
glove test. Safe to re-run: it deletes only its own previous collection.
"""
import math
import bmesh
import bpy
from mathutils import Vector

COL_NAME = "MaleBase"
X_OFFSET = 0.6

old = bpy.data.collections.get(COL_NAME)
if old:
    for ob in list(old.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    bpy.data.collections.remove(old)
col = bpy.data.collections.new(COL_NAME)
bpy.context.scene.collection.children.link(col)

bm = bmesh.new()
skin = bm.verts.layers.skin.verify()


K = 1.0   # size multiplier for the section being built (Skin shrinks radii)


def P(pos, rx, ry, root=False):
    """Add a skeleton point with cross-section half-sizes (rx, ry)."""
    v = bm.verts.new(Vector(pos))
    v[skin].radius = (rx * K, ry * K)
    if root:
        v[skin].use_root = True
    return v


def link(a, b):
    bm.edges.new((a, b))
    return b


def chain(start, points):
    prev = start
    for pos, rx, ry in points:
        prev = link(prev, P(pos, rx, ry))
    return prev


# ---- spine, neck, head --------------------------------------------------------
K = 1.45
pelvis = P((0, 0.010, 0.930), 0.150, 0.130, root=True)
waist_lo = link(pelvis, P((0, 0.000, 1.040), 0.128, 0.100))
waist = link(waist_lo, P((0, 0.000, 1.140), 0.118, 0.098))
chest = link(waist, P((0, -0.012, 1.320), 0.178, 0.140))
upper = link(chest, P((0, -0.004, 1.420), 0.190, 0.126))
neck_b = link(upper, P((0, 0.006, 1.500), 0.050, 0.052))
neck_t = link(neck_b, P((0, 0.004, 1.580), 0.046, 0.050))
h1 = link(neck_t, P((0, 0.000, 1.620), 0.070, 0.084))      # jaw
h2 = link(h1, P((0, -0.002, 1.695), 0.092, 0.112))         # skull widest
link(h2, P((0, 0.000, 1.800), 0.066, 0.082))


# ---- arms (A-pose, 30 degrees from the body) -------------------------------------
A = math.radians(30)


def arm(s):
    d = Vector((s * math.sin(A), 0, -math.cos(A)))          # along the arm
    n = Vector((-s * math.cos(A), 0, -math.sin(A)))         # palm normal (inward)
    w = Vector((0, 1, 0))                                   # front-back
    global K
    K = 1.35
    clav = link(upper, P((s * 0.115, 0.000, 1.470), 0.050, 0.070))
    sh_pos = Vector((s * 0.220, 0, 1.452))
    sh = link(clav, P(sh_pos, 0.066, 0.070))                # shoulder
    el_pos = sh_pos + d * 0.300
    wr_pos = el_pos + d * 0.255
    ua = link(sh, P(sh_pos + d * 0.140, 0.056, 0.058))      # biceps / triceps
    el = link(ua, P(el_pos, 0.043, 0.046))                  # elbow
    fa = link(el, P(el_pos + d * 0.110, 0.042, 0.044))      # forearm bulk
    wr = link(fa, P(wr_pos, 0.028, 0.025))                  # wrist
    # palm and four fingers (hands get a bigger multiplier)
    K = 1.3
    palm = link(wr, P(wr_pos + d * 0.062, 0.047, 0.024))
    offs = (-0.042, -0.014, 0.014, 0.040)                   # front first
    lens = (0.088, 0.096, 0.088, 0.071)
    for off, ln in zip(offs, lens):
        k = link(palm, P(wr_pos + d * 0.110 + w * off, 0.0100, 0.0095))
        a = 0.0
        p = Vector(k.co)
        r = 0.0098
        for frac, curl in ((0.43, 12), (0.30, 22), (0.27, 16)):
            a += math.radians(curl)
            p = p + (d * math.cos(a) + n * math.sin(a)) * (ln * frac)
            r *= 0.88
            k = link(k, P(p, r, r * 0.95))
    # thumb: front side, angled out from the palm
    tb = link(palm, P(wr_pos + d * 0.040 + w * -0.034, 0.015, 0.014))
    td = (d * 0.75 + w * -0.55 + n * 0.20).normalized()
    p = Vector(tb.co)
    r = 0.0140
    for ln in (0.046, 0.036, 0.032):
        p = p + td * ln
        r *= 0.88
        tb = link(tb, P(p, r, r))


arm(1)
arm(-1)


# ---- legs and feet ----------------------------------------------------------------
def leg(s):
    global K
    K = 1.22
    hip = link(pelvis, P((s * 0.088, 0.002, 0.915), 0.096, 0.096))
    th = link(hip, P((s * 0.093, -0.002, 0.720), 0.088, 0.092))     # thigh
    knee = link(th, P((s * 0.096, -0.004, 0.500), 0.056, 0.058))
    calf = link(knee, P((s * 0.098, 0.018, 0.360), 0.062, 0.074))
    ankle = link(calf, P((s * 0.098, 0.006, 0.090), 0.034, 0.036))
    heel = link(ankle, P((s * 0.098, 0.040, 0.046), 0.040, 0.040))   # heel
    mid = link(ankle, P((s * 0.100, -0.070, 0.050), 0.052, 0.044))   # foot arch
    link(mid, P((s * 0.102, -0.190, 0.034), 0.054, 0.036))           # toe box


leg(1)
leg(-1)

# ---- skin + subdivision -> smooth quad body ------------------------------------------
skel = bpy.data.meshes.new("MaleSkeleton_tmp")
bm.to_mesh(skel)
bm.free()
tmp = bpy.data.objects.new("MaleSkeleton_tmp", skel)
col.objects.link(tmp)
sk = tmp.modifiers.new("Skin", "SKIN")
sk.branch_smoothing = 1.0
sk.use_smooth_shade = True
ss = tmp.modifiers.new("Subsurf", "SUBSURF")
ss.levels = 2
ss.render_levels = 2

dg = bpy.context.evaluated_depsgraph_get()
body_mesh = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
body_mesh.name = "SM_MaleBase"
bpy.data.objects.remove(tmp, do_unlink=True)
bpy.data.meshes.remove(skel)

body = bpy.data.objects.new("SM_MaleBase", body_mesh)
col.objects.link(body)
body.location = (X_OFFSET, 0, 0)
try:
    body_mesh.shade_smooth()
except AttributeError:
    for p in body_mesh.polygons:
        p.use_smooth = True

mat = (bpy.data.materials.get("M_MaleBase_Skin")
       or bpy.data.materials.new("M_MaleBase_Skin"))
if not mat.node_tree:
    mat.use_nodes = True
bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
bsdf.inputs["Base Color"].default_value = (0.42, 0.34, 0.29, 1.0)
bsdf.inputs["Roughness"].default_value = 0.6
body.data.materials.append(mat)

# lock the base body layer: clothes go on top, never instead
body.lock_location = (True, True, True)
body.lock_rotation = (True, True, True)
body.lock_scale = (True, True, True)

# ---- report -----------------------------------------------------------------------------
body_mesh.calc_loop_triangles()
zs = [v.co.z for v in body_mesh.vertices]
xs = [v.co.x for v in body_mesh.vertices]
print(f"Male base v4: {len(body_mesh.polygons)} faces, "
      f"{len(body_mesh.loop_triangles)} tris")
print(f"  height {max(zs):.2f} m, width incl. arms {max(xs) - min(xs):.2f} m")
print("Tip: hover over the 3D window, press numpad period (.) to frame it.")
