"""Mid-Gauntlet v1 (support gear: recoil dampener) for the MHA RPG glove test.

Run inside Blender: Scripting tab -> New -> paste -> Run Script.
Real-world scale (1 unit = 1 m), forearm along +Z, wrist at z=0.
Builds into a collection called "MidGauntlet" with SM_ names and PBR materials.
Safe to re-run: it deletes only its own previous collection first.
"""
import math
import bmesh
import bpy
from mathutils import Matrix

COL_NAME = "MidGauntlet"

# ---- clean up only our own earlier run -------------------------------------
old = bpy.data.collections.get(COL_NAME)
if old:
    for ob in list(old.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    bpy.data.collections.remove(old)

col = bpy.data.collections.new(COL_NAME)
bpy.context.scene.collection.children.link(col)


# ---- materials -------------------------------------------------------------
def make_mat(name, color, metallic, roughness):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    if not m.node_tree:
        m.use_nodes = True
    bsdf = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    return m


M_FABRIC = make_mat("M_Gauntlet_Undersuit", (0.02, 0.025, 0.03, 1), 0.0, 0.85)
M_ARMOR = make_mat("M_Gauntlet_Armor", (0.12, 0.13, 0.15, 1), 0.9, 0.35)
M_DETAIL = make_mat("M_Gauntlet_Damper", (0.55, 0.57, 0.6, 1), 1.0, 0.25)


# ---- helpers ---------------------------------------------------------------

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

def smooth(ob):
    me = ob.data
    try:
        me.shade_smooth()
    except AttributeError:
        for p in me.polygons:
            p.use_smooth = True


def add_object(name, bm, mat):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    col.objects.link(ob)
    ob.data.materials.append(mat)
    smooth(ob)
    add_cyl_uv(me)
    return ob


def tube(name, r_bottom, r_top, z0, height, mat, thickness=0.004,
         bevel=0.0015, caps=False, segments=48):
    bm = bmesh.new()
    bmesh.ops.create_cone(
        bm, cap_ends=caps, cap_tris=False, segments=segments,
        radius1=r_bottom, radius2=r_top, depth=height,
        matrix=Matrix.Translation((0.0, 0.0, z0 + height / 2)),
    )
    ob = add_object(name, bm, mat)
    if thickness:
        s = ob.modifiers.new("Solidify", "SOLIDIFY")
        s.thickness = thickness
        s.offset = 1.0
    b = ob.modifiers.new("Bevel", "BEVEL")
    b.width = bevel
    b.segments = 3
    b.limit_method = "ANGLE"
    b.harden_normals = True
    w = ob.modifiers.new("WeightedNormal", "WEIGHTED_NORMAL")
    w.keep_sharp = True
    return ob


def radius_at(z, z0, z1, r0, r1):
    return r0 + (r1 - r0) * (z - z0) / (z1 - z0)


# ---- the parts -------------------------------------------------------------
# Undersuit sleeve: wrist -> elbow
tube("SM_Gauntlet_Undersuit", 0.040, 0.052, 0.0, 0.28, M_FABRIC,
     thickness=0.003, bevel=0.0008)

# Armor shell over the mid forearm
A_Z0, A_Z1, A_R0, A_R1 = 0.06, 0.24, 0.050, 0.060
tube("SM_Gauntlet_ArmorShell", A_R0, A_R1, A_Z0, A_Z1 - A_Z0, M_ARMOR,
     thickness=0.006, bevel=0.002)

# Rim rings at both ends of the shell
tube("SM_Gauntlet_RimLow", A_R0 + 0.004, A_R0 + 0.004, A_Z0 - 0.006, 0.014,
     M_DETAIL, thickness=0.004, bevel=0.0015)
tube("SM_Gauntlet_RimHigh", A_R1 + 0.004, A_R1 + 0.004, A_Z1 - 0.008, 0.014,
     M_DETAIL, thickness=0.004, bevel=0.0015)

# Straps at wrist and upper forearm
tube("SM_Gauntlet_StrapWrist", 0.0433, 0.0443, 0.015, 0.025, M_FABRIC,
     thickness=0.004, bevel=0.001)
tube("SM_Gauntlet_StrapUpper", 0.0537, 0.0548, 0.25, 0.025, M_FABRIC,
     thickness=0.004, bevel=0.001)

# Six recoil dampers (hydraulic rods) around the shell
mid_z = (A_Z0 + A_Z1) / 2
rod_len = 0.14
rod_r = 0.006
ring_r = radius_at(mid_z, A_Z0, A_Z1, A_R0, A_R1) + 0.006 + rod_r
for i in range(6):
    a = math.tau * i / 6
    bm = bmesh.new()
    bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=16,
        radius1=rod_r, radius2=rod_r, depth=rod_len,
        matrix=Matrix.Translation(
            (ring_r * math.cos(a), ring_r * math.sin(a), mid_z)),
    )
    ob = add_object(f"SM_Gauntlet_Damper_{i + 1:02d}", bm, M_DETAIL)
    b = ob.modifiers.new("Bevel", "BEVEL")
    b.width = 0.0012
    b.segments = 2
    b.limit_method = "ANGLE"

# ---- report ----------------------------------------------------------------
tris = 0
dg = bpy.context.evaluated_depsgraph_get()
for ob in col.objects:
    ev = ob.evaluated_get(dg)
    me = ev.to_mesh()
    me.calc_loop_triangles()
    tris += len(me.loop_triangles)
    ev.to_mesh_clear()
print(f"Mid-Gauntlet v1: {len(col.objects)} objects, {tris} tris")
print("Tip: hover over the 3D window and press Home to see it.")
