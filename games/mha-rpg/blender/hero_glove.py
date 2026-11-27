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
EASE = 0.0015                # gap between skin and glove (m)
THICKNESS = 0.002            # glove fabric thickness (m)
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
# open the glove at the wrist: remove everything above the cuff line
doomed = [f for f in bm.faces if all(v.co.z > CUFF_Z for v in f.verts)]
bmesh.ops.delete(bm, geom=doomed, context="FACES")
loose = [v for v in bm.verts if not v.link_faces]
bmesh.ops.delete(bm, geom=loose, context="VERTS")

me = bpy.data.meshes.new("SM_HeroGlove")
bm.to_mesh(me)
bm.free()
glove = bpy.data.objects.new("SM_HeroGlove", me)
col.objects.link(glove)
glove.data.materials.append(M_FABRIC)
smooth(me)
sol = glove.modifiers.new("Thickness", "SOLIDIFY")
sol.thickness = THICKNESS
sol.offset = 1.0                         # grow outward, inner face stays put
sub = glove.modifiers.new("Subsurf", "SUBSURF")
sub.levels = 1
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
    ellipsoid("SM_Glove_PalmGrip", pos, nrm, (0.026, 0.034, 0.003), M_GRIP)

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
