"""Male base mesh v1 (stylized mannequin) for the MHA RPG.

Run inside Blender: Scripting tab -> New -> paste -> Run Script.
Real-world scale (1 unit = 1 m), 1.80 m tall, faces -Y, A-pose so clothes and
rigging are easy later. Bald, faceless, no clothing: this is the BASE BODY
layer. Clothing is built as separate objects on top, later.

It is placed 0.6 m to the side (+X) so it does not overlap the glove test.
Safe to re-run: it deletes only its own previous collection.
"""
import math
import bmesh
import bpy
from mathutils import Matrix, Vector

COL_NAME = "MaleBase"
X_OFFSET = 0.6
VOXEL = 0.006

old = bpy.data.collections.get(COL_NAME)
if old:
    for ob in list(old.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    bpy.data.collections.remove(old)
col = bpy.data.collections.new(COL_NAME)
bpy.context.scene.collection.children.link(col)

bm = bmesh.new()


def V(x, y, z):
    return Vector((x, y, z))


def sphere(p, r):
    bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=12, radius=r,
                              matrix=Matrix.Translation(p))


def blob(p, radii, axes=None):
    """Ellipsoid at p with radii (x, y, z); axes = optional 3x3 rotation."""
    m = Matrix.Translation(p)
    if axes is not None:
        m = m @ axes.to_4x4()
    m = m @ Matrix.Diagonal((radii[0], radii[1], radii[2], 1.0))
    bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=12, radius=1.0,
                              matrix=m)


def capsule(p0, p1, r0, r1):
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    rot = Vector((0, 0, 1)).rotation_difference(d).to_matrix().to_4x4()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=24,
                          radius1=r0, radius2=r1, depth=d.length,
                          matrix=Matrix.Translation((p0 + p1) / 2) @ rot)
    sphere(p0, r0)
    sphere(p1, r1)


def tube_path(p0, p1, r0, r1, bulge=0.0, peak=0.75, step=0.010):
    """Chain of overlapping spheres from p0 to p1: a smooth tapered limb with
    an optional muscle bulge (biceps, calf). No beads, no ridges."""
    p0, p1 = Vector(p0), Vector(p1)
    n = max(2, int((p1 - p0).length / step))
    for i in range(n + 1):
        t = i / n
        r = (r0 + (r1 - r0) * t) * (1.0 + bulge * math.sin(math.pi * t ** peak))
        sphere(p0.lerp(p1, t), r)


# ---- head and neck (faceless mannequin head) ---------------------------------
blob(V(0, 0, 1.690), (0.089, 0.106, 0.118))        # skull
blob(V(0, -0.006, 1.628), (0.070, 0.080, 0.070))   # jaw / chin
capsule(V(0, 0.004, 1.600), V(0, 0, 1.500), 0.055, 0.064)   # neck

# ---- torso: one smooth loft (no stacked balloons) -----------------------------
# (z, half-width x, half-depth y). Shoulders widest, narrow waist, hips narrower
# than the shoulders (male proportions).
TORSO = [
    (1.50, 0.150, 0.085),
    (1.46, 0.215, 0.092),
    (1.40, 0.195, 0.108),
    (1.32, 0.178, 0.114),
    (1.24, 0.162, 0.108),
    (1.16, 0.146, 0.098),
    (1.08, 0.138, 0.094),
    (1.00, 0.146, 0.099),
    (0.94, 0.154, 0.104),
    (0.88, 0.150, 0.100),
    (0.84, 0.140, 0.092),
]


def torso_at(z):
    for (z0, x0, y0), (z1, x1, y1) in zip(TORSO, TORSO[1:]):
        if z1 <= z <= z0:
            t = (z0 - z) / (z0 - z1)
            return x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
    return None


z = 1.50
while z >= 0.84:
    w = torso_at(z)
    if w:
        blob(V(0, 0.004 if z < 1.1 else 0, z), (w[0], w[1], 0.030))
    z -= 0.008                                         # fine steps: no ridges
blob(V(0.068, 0.045, 0.920), (0.074, 0.068, 0.080))    # glute R
blob(V(-0.068, 0.045, 0.920), (0.074, 0.068, 0.080))   # glute L
blob(V(0.080, -0.085, 1.370), (0.088, 0.046, 0.070))   # pec R
blob(V(-0.080, -0.085, 1.370), (0.088, 0.046, 0.070))  # pec L

# ---- arms (A-pose, 30 degrees from the body), built for both sides ----------
A = math.radians(30)


def basis(d, n, w):
    """Rotation matrix whose columns are the local axes (w, n, d)."""
    return Matrix((w, n, d)).transposed()


def arm(side):
    s = 1 if side == "R" else -1
    d = V(s * math.sin(A), 0, -math.cos(A))            # along the arm
    n = V(-s * math.cos(A), 0, -math.sin(A))           # palm normal (inward)
    w = V(0, 1, 0)                                     # front-back axis
    sh = V(s * 0.205, 0, 1.455)
    el = sh + d * 0.300
    wr = el + d * 0.255
    # smooth arm: joint spheres match the limb radius (no beads)
    sphere(sh, 0.066)                                  # shoulder cap (deltoid)
    tube_path(sh, el, 0.060, 0.044, bulge=0.10, peak=0.6)    # upper arm
    tube_path(el, wr, 0.045, 0.030, bulge=0.12, peak=0.45)   # forearm
    # hand (bigger, fuller)
    palm_c = wr + d * 0.052
    blob(palm_c, (0.056, 0.024, 0.064), Matrix((w, n, d)).transposed())
    offs = (-0.033, -0.011, 0.011, 0.032)              # toward front first
    lens = (0.088, 0.096, 0.088, 0.071)
    for off, ln in zip(offs, lens):
        p = wr + d * 0.110 + w * off
        a = 0.0
        r = 0.0138
        for frac, curl in ((0.43, 12), (0.30, 22), (0.27, 16)):
            a += math.radians(curl)
            q = p + (d * math.cos(a) + n * math.sin(a)) * (ln * frac)
            capsule(p, q, r, r * 0.86)
            p, r = q, r * 0.86
    # thumb: front side, angled out from the palm
    tb = wr + d * 0.034 + w * -0.034
    td = (d * 0.75 + w * -0.55 + n * 0.20).normalized()
    p, r = tb, 0.0175
    for ln in (0.046, 0.036, 0.032):
        q = p + td * ln
        capsule(p, q, r, r * 0.86)
        p, r = q, r * 0.86


arm("R")
arm("L")

# ---- legs ---------------------------------------------------------------------


def leg(side):
    s = 1 if side == "R" else -1
    hip = V(s * 0.090, 0, 0.930)
    knee = V(s * 0.095, -0.004, 0.500)
    ankle = V(s * 0.097, 0.006, 0.088)
    tube_path(hip, knee, 0.098, 0.064, bulge=0.07, peak=0.55)    # thigh
    tube_path(knee, ankle, 0.064, 0.040, bulge=0.16, peak=0.50)  # shin + calf
    # foot (toes point -Y), longer and fuller
    blob(V(s * 0.097, 0.040, 0.048), (0.047, 0.054, 0.048))     # heel
    blob(V(s * 0.099, -0.060, 0.070), (0.044, 0.095, 0.036))    # instep
    capsule(V(s * 0.097, 0.000, 0.056), V(s * 0.100, -0.185, 0.040), 0.048, 0.040)
    blob(V(s * 0.101, -0.208, 0.034), (0.047, 0.046, 0.032))    # toe box


leg("R")
leg("L")

# ---- merge into one smooth body -----------------------------------------------
parts = bpy.data.meshes.new("MaleParts_tmp")
bm.to_mesh(parts)
bm.free()
tmp = bpy.data.objects.new("MaleParts_tmp", parts)
col.objects.link(tmp)
rm = tmp.modifiers.new("Merge", "REMESH")
rm.mode = "VOXEL"
rm.voxel_size = VOXEL
sm = tmp.modifiers.new("Smooth", "SMOOTH")
sm.factor = 0.8
sm.iterations = 10

dg = bpy.context.evaluated_depsgraph_get()
body_mesh = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
body_mesh.name = "SM_MaleBase"
bpy.data.objects.remove(tmp, do_unlink=True)
bpy.data.meshes.remove(parts)

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

# ---- report -------------------------------------------------------------------
body_mesh.calc_loop_triangles()
zs = [v.co.z for v in body_mesh.vertices]
xs = [v.co.x for v in body_mesh.vertices]
print(f"Male base v3: {len(body_mesh.polygons)} faces, "
      f"{len(body_mesh.loop_triangles)} tris")
print(f"  height {max(zs):.2f} m, width incl. arms {max(xs) - min(xs):.2f} m")
print("Tip: hover over the 3D window, press numpad period (.) to frame it.")
