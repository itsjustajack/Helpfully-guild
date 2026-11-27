"""Hero glove v1 for the MHA RPG glove test.

Run inside Blender AFTER the hand exists (hand_base.py, or an MPFB hand).
Scripting tab -> New -> paste -> Run Script.

It fits to ANY hand object: change TARGET below to your hand's name.
Hand layout expected (same as hand_base.py): wrist at z=0, hand hangs toward
-Z, palm faces -Y, back of hand faces +Y, real-world metres.

The glove is the hand surface pushed out by EASE, opened at the wrist, then
given thickness. Armour knuckle plates and a palm grip pad are placed on the
real surface by ray casting, so they sit on the hand instead of floating.
Safe to re-run: it deletes only its own previous collection.
"""
import bmesh
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

TARGET = "SM_HandBase_R"     # name of the hand object to fit to
EASE = 0.0010                # gap between skin and glove (m)
THICKNESS = 0.0012           # glove fabric thickness (m)
CUFF_Z = 0.028               # glove opens at this height above the wrist (m)
COL_NAME = "HeroGlove"

hand = bpy.data.objects.get(TARGET)
if hand is None:
    raise SystemExit(f"No object named {TARGET!r}. Run hand_base.py first, "
                     "or set TARGET to your hand's name.")

old = bpy.data.collections.get(COL_NAME)
if old:
    for ob in list(old.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    bpy.data.collections.remove(old)
col = bpy.data.collections.new(COL_NAME)
bpy.context.scene.collection.children.link(col)


# ---- materials (reuse the gauntlet's if they exist) ---------------------------
def make_mat(name, color, metallic, roughness):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    if not m.node_tree:
        m.use_nodes = True
    bsdf = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    return m


M_FABRIC = make_mat("M_Glove_Fabric", (0.025, 0.03, 0.035, 1), 0.0, 0.8)
M_ARMOR = make_mat("M_Gauntlet_Armor", (0.12, 0.13, 0.15, 1), 0.9, 0.35)
M_GRIP = make_mat("M_Glove_Grip", (0.01, 0.01, 0.012, 1), 0.0, 0.95)


def add_cyl_uv(me):
    """Simple cylindrical UV map around Z (placeholder until proper unwrap)."""
    import math as _m
    if me.uv_layers:
        return
    zs = [v.co.z for v in me.vertices] or [0.0]
    z0, z1 = min(zs), max(zs)
    span = (z1 - z0) or 1.0
    uv = me.uv_layers.new(name="UVMap")
    for poly in me.polygons:
        flat_cap = abs(poly.normal.z) > 0.9      # end caps: project from above
        for li in poly.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            if flat_cap:
                uv.data[li].uv = (co.x * 4.0 + 0.5, co.y * 4.0 + 0.5)
            else:
                uv.data[li].uv = (_m.atan2(co.x, co.y) / _m.tau + 0.5, (co.z - z0) / span)


def smooth(me):
    try:
        me.shade_smooth()
    except AttributeError:
        for p in me.polygons:
            p.use_smooth = True


# ---- 1. glove shell from the hand surface -------------------------------------
dg = bpy.context.evaluated_depsgraph_get()
src = bpy.data.meshes.new_from_object(hand.evaluated_get(dg))
src.transform(hand.matrix_world)

bm = bmesh.new()
bm.from_mesh(src)
bm.normal_update()
for v in bm.verts:                       # push out by EASE along the normal
    v.co += v.normal * EASE
# fuse the pushed-out surface into ONE clean shell (no overlaps between fingers)
_fm = bpy.data.meshes.new("GloveFuse_tmp")
bm.to_mesh(_fm)
bm.free()
_fo = bpy.data.objects.new("GloveFuse_tmp", _fm)
col.objects.link(_fo)
_r = _fo.modifiers.new("Fuse", "REMESH")
_r.mode = "VOXEL"
_r.voxel_size = 0.0012
_d = _fo.modifiers.new("Budget", "DECIMATE")
_d.ratio = 0.12
_fused = bpy.data.meshes.new_from_object(_fo.evaluated_get(bpy.context.evaluated_depsgraph_get()))
bpy.data.objects.remove(_fo, do_unlink=True)
bpy.data.meshes.remove(_fm)
bm = bmesh.new()
bm.from_mesh(_fused)
bpy.data.meshes.remove(_fused)

# open the glove at the wrist: remove everything above the cuff line
doomed = [f for f in bm.faces if all(v.co.z > CUFF_Z for v in f.verts)]
bmesh.ops.delete(bm, geom=doomed, context="FACES")
loose = [v for v in bm.verts if not v.link_faces]
bmesh.ops.delete(bm, geom=loose, context="VERTS")

bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)   # weld seams
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)          # consistent winding
me = bpy.data.meshes.new("SM_HeroGlove")
bm.to_mesh(me)
bm.free()
glove = bpy.data.objects.new("SM_HeroGlove", me)
col.objects.link(glove)
glove.data.materials.append(M_FABRIC)
add_cyl_uv(me)
smooth(me)
sol = glove.modifiers.new("Thickness", "SOLIDIFY")
sol.thickness = THICKNESS
sol.offset = 1.0                         # grow outward, inner face stays put
sol.use_even_offset = True               # even thickness, no folding
sol.use_quality_normals = True
bpy.data.meshes.remove(src)

# ---- 2. armour knuckle plates + palm grip pad, placed by ray casting ---------
hand_inv = hand.matrix_world.inverted()


def hit_surface(x, z, from_y):
    """Ray-cast onto the hand from +Y (back) or -Y (palm). Returns (pos, normal)."""
    origin = hand_inv @ Vector((x, from_y, z))
    direction = hand_inv.to_3x3() @ Vector((0, -1 if from_y > 0 else 1, 0))
    ok, loc, nrm, _ = hand.ray_cast(origin, direction)
    if not ok:
        return None
    return (hand.matrix_world @ loc,
            (hand.matrix_world.to_3x3() @ nrm).normalized())


def ellipsoid(name, pos, normal, size, mat, bevel=False):
    rot = Vector((0, 0, 1)).rotation_difference(normal).to_matrix().to_4x4()
    b = bmesh.new()
    bmesh.ops.create_uvsphere(
        b, u_segments=24, v_segments=12, radius=1.0,
        matrix=(Matrix.Translation(pos + normal * (EASE + THICKNESS)) @ rot
                @ Matrix.Diagonal((size[0], size[1], size[2], 1.0))),
    )
    m = bpy.data.meshes.new(name)
    b.to_mesh(m)
    b.free()
    ob = bpy.data.objects.new(name, m)
    col.objects.link(ob)
    ob.data.materials.append(mat)
    smooth(m)
    add_cyl_uv(m)
    return ob


plates = 0
for i, x in enumerate((-0.030, -0.010, 0.010, 0.028)):
    hit = hit_surface(x, -0.090, 0.15)
    if hit:
        pos, nrm = hit
        ellipsoid(f"SM_Glove_KnucklePlate_{i + 1:02d}", pos, nrm,
                  (0.0105, 0.0125, 0.0035), M_ARMOR)
        plates += 1

grip = hit_surface(0.0, -0.050, -0.15)
if grip:
    pos, nrm = grip
    ellipsoid("SM_Glove_PalmGrip", pos - nrm * (EASE + THICKNESS), nrm,
              (0.026, 0.034, 0.0055), M_GRIP)   # sunk in: crosses the glove, no flicker

# ---- 3. fit report ------------------------------------------------------------
bvh = BVHTree.FromObject(glove, bpy.context.evaluated_depsgraph_get())
gaps = []
for v in hand.data.vertices:
    p = hand.matrix_world @ v.co
    if p.z < CUFF_Z - 0.01:
        loc, _, _, dist = bvh.find_nearest(p)
        if loc is not None:
            gaps.append(dist)
too_close = sum(1 for g in gaps if g < EASE * 0.5)
print(f"Hero glove v1 fitted to {TARGET}")
print(f"  knuckle plates: {plates}, palm grip: {'yes' if grip else 'no'}")
if gaps:
    print(f"  smallest gap skin->glove: {min(gaps) * 1000:.2f} mm "
          f"(aim for about {EASE * 1000:.1f} mm)")
    print(f"  places where glove is touching skin: {too_close} (aim for 0)")
print("Tip: hover over the 3D window and press Home to see it.")
