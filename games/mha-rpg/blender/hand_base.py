"""Hand base v1 (right hand) for the MHA RPG glove test.

Run inside Blender: Scripting tab -> New -> paste -> Run Script.
Real-world scale (1 unit = 1 m). Forearm along +Z, wrist at z=0, hand hangs
down toward -Z, palm faces -Y, thumb on the -X side (right hand, anatomical
position). The Mid-Gauntlet from mid_gauntlet.py slides over the wrist.

This is the locked BASE BODY layer: bald, smooth, no clothes. The glove goes
on top of it. Safe to re-run: it deletes only its own previous collection.
"""
import math
import bmesh
import bpy
from mathutils import Matrix, Vector

COL_NAME = "HandBase"

old = bpy.data.collections.get(COL_NAME)
if old:
    for ob in list(old.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    bpy.data.collections.remove(old)

col = bpy.data.collections.new(COL_NAME)
bpy.context.scene.collection.children.link(col)

bm = bmesh.new()


def sphere(p, r):
    bmesh.ops.create_uvsphere(
        bm, u_segments=24, v_segments=12, radius=r,
        matrix=Matrix.Translation(p),
    )


def capsule(p0, p1, r0, r1):
    """Tapered capsule from p0 (radius r0) to p1 (radius r1)."""
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    rot = Vector((0, 0, 1)).rotation_difference(d).to_matrix().to_4x4()
    bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=24,
        radius1=r0, radius2=r1, depth=d.length,
        matrix=Matrix.Translation((p0 + p1) / 2) @ rot,
    )
    sphere(p0, r0)
    sphere(p1, r1)


def squashed_cone(z_bottom, z_top, r_bottom, r_top, y_scale):
    """Elliptical cone along Z (used for forearm stub, wrist and palm)."""
    depth = z_top - z_bottom
    m = (Matrix.Translation((0, 0, (z_top + z_bottom) / 2))
         @ Matrix.Diagonal((1.0, y_scale, 1.0, 1.0)))
    bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=32,
        radius1=r_bottom, radius2=r_top, depth=depth, matrix=m,
    )


# ---- forearm stub (so the gauntlet has something to sit on) + wrist + palm --
squashed_cone(0.0, 0.10, 0.029, 0.031, 0.75)      # forearm stub
squashed_cone(-0.095, 0.0, 0.044, 0.029, 0.55)    # palm: wrist -> knuckles

# ---- four fingers -----------------------------------------------------------
KNUCKLE_Z = -0.092
# (x position, total length, base radius, curl multiplier)
FINGERS = [
    (-0.030, 0.072, 0.0095, 1.0),   # index
    (-0.010, 0.080, 0.0100, 1.0),   # middle
    (0.010, 0.073, 0.0095, 1.0),    # ring
    (0.028, 0.058, 0.0082, 1.0),    # pinky
]
SPLIT = (0.43, 0.30, 0.27)          # proximal, middle, distal
CURL = (10, 20, 15)                 # degrees, relaxed natural curl

for x, length, r, curlk in FINGERS:
    p = Vector((x, -0.004, KNUCKLE_Z))
    sphere(p, r * 1.12)                       # knuckle
    angle = 0.0
    radius = r
    for seg_frac, curl in zip(SPLIT, CURL):
        angle += math.radians(curl) * curlk
        d = Vector((0, -math.sin(angle), -math.cos(angle))) * (length * seg_frac)
        q = p + d
        r_end = radius * 0.84
        capsule(p, q, radius, r_end)
        p, radius = q, r_end

# ---- thumb (on the -X side) -------------------------------------------------
T = [
    ((-0.022, -0.006, -0.018), 0.0125),
    ((-0.048, -0.020, -0.058), 0.0112),
    ((-0.060, -0.030, -0.086), 0.0098),
    ((-0.064, -0.036, -0.108), 0.0082),
]
for (a, ra), (b, rb) in zip(T, T[1:]):
    capsule(a, b, ra, rb)

# ---- merge into one smooth surface -------------------------------------------
parts_mesh = bpy.data.meshes.new("HandParts_tmp")
bm.to_mesh(parts_mesh)
bm.free()
tmp = bpy.data.objects.new("HandParts_tmp", parts_mesh)
col.objects.link(tmp)

rm = tmp.modifiers.new("Merge", "REMESH")
rm.mode = "VOXEL"
rm.voxel_size = 0.0015
sm = tmp.modifiers.new("Smooth", "SMOOTH")
sm.factor = 1.0
sm.iterations = 10

dg = bpy.context.evaluated_depsgraph_get()
final_mesh = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
final_mesh.name = "SM_HandBase_R"

bpy.data.objects.remove(tmp, do_unlink=True)
bpy.data.meshes.remove(parts_mesh)

hand = bpy.data.objects.new("SM_HandBase_R", final_mesh)
col.objects.link(hand)
try:
    final_mesh.shade_smooth()
except AttributeError:
    for poly in final_mesh.polygons:
        poly.use_smooth = True

# ---- skin material (placeholder tone, full PBR inputs) ------------------------
mat = bpy.data.materials.get("M_HandBase_Skin") or bpy.data.materials.new("M_HandBase_Skin")
if not mat.node_tree:
    mat.use_nodes = True
bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
bsdf.inputs["Base Color"].default_value = (0.55, 0.38, 0.30, 1.0)
bsdf.inputs["Roughness"].default_value = 0.5
for sss_name in ("Subsurface Weight", "Subsurface"):
    if sss_name in bsdf.inputs:
        bsdf.inputs[sss_name].default_value = 0.05
        break
hand.data.materials.append(mat)

# ---- lock the base body layer -------------------------------------------------
hand.lock_location = (True, True, True)
hand.lock_rotation = (True, True, True)
hand.lock_scale = (True, True, True)

# ---- report -------------------------------------------------------------------
final_mesh.calc_loop_triangles()
zs = [v.co.z for v in final_mesh.vertices]
print(f"Hand base v1: {len(final_mesh.polygons)} faces, "
      f"{len(final_mesh.loop_triangles)} tris")
print(f"Hand length wrist->fingertip: {abs(min(zs)) * 100:.1f} cm "
      f"(typical adult 17-20 cm)")
print("Tip: hover over the 3D window and press Home to see it.")
