"""Hero Office: a cosy isometric cutaway room (HD-2D look) for the pixel game.

Run inside Blender: Scripting tab -> New -> paste -> Run Script.
Everything is built from simple shapes + procedural materials: free, no AI
art, no copied art. Real-world scale (1 unit = 1 m). Room is 6 x 5 m, walls 3 m.
Two back walls are kept, the front two are cut away (low brick wall left),
seen from a true isometric orthographic camera. Pixel hero stands inside
(billboard with texel-locked pixels), lit by warm lamps and cool window light.

Safe to re-run: it deletes only its own previous collection.
"""
import math
import os
import random
import runpy

import bmesh
import bpy
from mathutils import Matrix, Vector

COL = "HeroOffice"
HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else ""
SPRITE = os.path.join(HERE, "..", "..", "..", "pixel-hero", "hero_sheet.png")
random.seed(11)
CHAR_MODE = "3d"          # "3d": painted-style 3D characters, or "sprite": pixel billboard

old = bpy.data.collections.get(COL)
if old:
    for ob in list(old.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    bpy.data.collections.remove(old)
col = bpy.data.collections.new(COL)
bpy.context.scene.collection.children.link(col)


# ---- materials ---------------------------------------------------------------
def new_mat(name):
    m = bpy.data.materials.get(name)
    if m:
        bpy.data.materials.remove(m)
    m = bpy.data.materials.new(name)
    if not m.node_tree:
        m.use_nodes = True
    return m


def principled(m):
    return next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")


def set_in(node, name, value):
    if name in node.inputs:
        node.inputs[name].default_value = value


def flat(name, color, rough=0.6, metal=0.0, emit=None, strength=0.0):
    m = new_mat(name)
    b = principled(m)
    set_in(b, "Base Color", (*color, 1))
    set_in(b, "Roughness", rough)
    set_in(b, "Metallic", metal)
    if emit:
        set_in(b, "Emission Color", (*emit, 1))
        set_in(b, "Emission Strength", strength)
    return m


def planks(name, c1, c2, mortar, width=1.4, height=0.16, rough=0.5, bump=0.35):
    m = new_mat(name)
    nt = m.node_tree
    b = principled(m)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    br = nt.nodes.new("ShaderNodeTexBrick")
    br.offset = 0.5
    br.offset_frequency = 2
    set_in(br, "Color1", (*c1, 1))
    set_in(br, "Color2", (*c2, 1))
    set_in(br, "Mortar", (*mortar, 1))
    set_in(br, "Scale", 1.0)
    set_in(br, "Mortar Size", 0.012)
    set_in(br, "Brick Width", width)
    set_in(br, "Row Height", height)
    nz = nt.nodes.new("ShaderNodeTexNoise")
    set_in(nz, "Scale", 18.0)
    set_in(nz, "Detail", 6.0)
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.blend_type = "MULTIPLY"
    set_in(mix, "Factor", 0.35)
    bm = nt.nodes.new("ShaderNodeBump")
    set_in(bm, "Strength", bump)
    nt.links.new(tc.outputs["Object"], br.inputs["Vector"])
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    nt.links.new(br.outputs["Color"], mix.inputs[6])
    nt.links.new(nz.outputs["Color"], mix.inputs[7])
    nt.links.new(mix.outputs[2], b.inputs["Base Color"])
    nt.links.new(br.outputs["Fac"], bm.inputs["Height"])
    nt.links.new(bm.outputs["Normal"], b.inputs["Normal"])
    set_in(b, "Roughness", rough)
    return m


def plaster(name, c1, c2, rough=0.85):
    m = new_mat(name)
    nt = m.node_tree
    b = principled(m)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise")
    set_in(nz, "Scale", 9.0)
    set_in(nz, "Detail", 10.0)
    cr = nt.nodes.new("ShaderNodeValToRGB")
    cr.color_ramp.elements[0].color = (*c1, 1)
    cr.color_ramp.elements[1].color = (*c2, 1)
    bm = nt.nodes.new("ShaderNodeBump")
    set_in(bm, "Strength", 0.2)
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    nt.links.new(nz.outputs["Fac"], cr.inputs["Fac"])
    nt.links.new(cr.outputs["Color"], b.inputs["Base Color"])
    nt.links.new(nz.outputs["Fac"], bm.inputs["Height"])
    nt.links.new(bm.outputs["Normal"], b.inputs["Normal"])
    set_in(b, "Roughness", rough)
    return m


M = {
    "floor": planks("M_Floor", (0.30, 0.17, 0.08), (0.22, 0.12, 0.06), (0.05, 0.03, 0.015)),
    "plaster": plaster("M_Plaster", (0.55, 0.42, 0.28), (0.70, 0.56, 0.38)),
    "wainscot": planks("M_Wainscot", (0.16, 0.09, 0.05), (0.12, 0.07, 0.04), (0.03, 0.02, 0.01),
                       width=0.5, height=0.5, bump=0.3),
    "brick": planks("M_Brick", (0.42, 0.20, 0.14), (0.34, 0.15, 0.11), (0.30, 0.27, 0.24),
                    width=0.25, height=0.075, rough=0.85, bump=0.6),
    "darkwood": flat("M_DarkWood", (0.10, 0.06, 0.035), 0.55),
    "midwood": flat("M_MidWood", (0.26, 0.15, 0.07), 0.5),
    "gold": flat("M_Gold", (0.9, 0.65, 0.2), 0.3, 1.0),
    "paper": flat("M_Paper", (0.85, 0.80, 0.68), 0.9),
    "cork": flat("M_Cork", (0.45, 0.30, 0.16), 0.95),
    "green": flat("M_GreenShade", (0.05, 0.22, 0.15), 0.35, 0.3),
    "rug": plaster("M_Rug", (0.10, 0.22, 0.24), (0.18, 0.32, 0.30), 0.95),
    "rugedge": flat("M_RugEdge", (0.45, 0.22, 0.12), 0.95),
    "leaf": flat("M_Leaf", (0.07, 0.28, 0.08), 0.6),
    "pot": flat("M_Pot", (0.38, 0.17, 0.10), 0.7),
    "metal": flat("M_Cabinet", (0.14, 0.20, 0.19), 0.45, 0.6),
    "bulb": flat("M_Bulb", (1, 0.8, 0.5), 0.3, emit=(1.0, 0.62, 0.25), strength=14.0),
    "window": flat("M_Window", (0.5, 0.65, 0.9), 0.1, emit=(0.45, 0.6, 1.0), strength=1.1),
    "lantern": flat("M_Lantern", (1, 0.8, 0.5), 0.3, emit=(1.0, 0.6, 0.2), strength=9.0),
    "sign": flat("M_Sign", (0.92, 0.72, 0.25), 0.35, 0.8),
}
BOXES = [flat(f"M_Archive{i}", c, 0.8) for i, c in enumerate([
    (0.22, 0.30, 0.30), (0.45, 0.33, 0.20), (0.33, 0.20, 0.11),
    (0.55, 0.45, 0.30), (0.22, 0.27, 0.20), (0.30, 0.35, 0.42)])]
BOOKS = [flat(f"M_Book{i}", c, 0.7) for i, c in enumerate([
    (0.10, 0.30, 0.18), (0.45, 0.10, 0.10), (0.30, 0.22, 0.10)])]


# ---- helpers ------------------------------------------------------------------
def finish(ob, mat, bevel=0.0, smooth=True):
    col.objects.link(ob)
    ob.data.materials.append(mat)
    if smooth:
        try:
            ob.data.shade_smooth()
        except AttributeError:
            pass
    if bevel:
        b = ob.modifiers.new("Bevel", "BEVEL")
        b.width = bevel
        b.segments = 2
        b.limit_method = "ANGLE"
    return ob


def box(name, size, loc, mat, rot=(0, 0, 0), bevel=0.008):
    b = bmesh.new()
    bmesh.ops.create_cube(b, size=1.0, matrix=Matrix.Diagonal((*size, 1.0)))
    me = bpy.data.meshes.new(name)
    b.to_mesh(me)
    b.free()
    ob = bpy.data.objects.new(name, me)
    ob.location = loc
    ob.rotation_euler = rot
    me.shade_flat()
    return finish(ob, mat, min(bevel, min(size) * 0.45), smooth=False)   # flat: no dark corner artifacts


def cyl(name, r1, r2, h, loc, mat, seg=24, rot=(0, 0, 0)):
    b = bmesh.new()
    bmesh.ops.create_cone(b, cap_ends=True, segments=seg, radius1=r1, radius2=r2, depth=h)
    me = bpy.data.meshes.new(name)
    b.to_mesh(me)
    b.free()
    ob = bpy.data.objects.new(name, me)
    ob.location = loc
    ob.rotation_euler = rot
    return finish(ob, mat)


def ball(name, r, loc, mat, scale=(1, 1, 1), rot=(0, 0, 0)):
    b = bmesh.new()
    bmesh.ops.create_uvsphere(b, u_segments=20, v_segments=10, radius=r,
                              matrix=Matrix.Diagonal((*scale, 1.0)))
    me = bpy.data.meshes.new(name)
    b.to_mesh(me)
    b.free()
    ob = bpy.data.objects.new(name, me)
    ob.location = loc
    ob.rotation_euler = rot
    return finish(ob, mat)


def light(name, kind, loc, color, power, size=0.1, rot=(0, 0, 0)):
    ld = bpy.data.lights.new(name, kind)
    ld.color = color
    ld.energy = power
    if kind == "POINT":
        ld.shadow_soft_size = size
    if kind == "AREA":
        ld.size = size
    ob = bpy.data.objects.new(name, ld)
    ob.location = loc
    ob.rotation_euler = rot
    col.objects.link(ob)
    return ob


# ---- shell: floor, two back walls, low brick front walls --------------------------
RX, RY, RH = 6.0, 5.0, 3.0
box("SM_Floor", (RX + 0.4, RY + 0.4, 0.2), (RX / 2, RY / 2, -0.1), M["floor"])
box("SM_WallBack", (RX + 0.4, 0.2, RH), (RX / 2, RY + 0.1, RH / 2), M["plaster"])
box("SM_WallLeft", (0.2, RY + 0.2, RH), (-0.1, (RY - 0.2) / 2, RH / 2), M["plaster"])
box("SM_BrickFront", (RX + 0.4, 0.22, 0.45), (RX / 2, -0.1, 0.225), M["brick"])
box("SM_BrickRight", (0.22, RY + 0.4, 0.45), (RX + 0.1, RY / 2, 0.225), M["brick"])
for nm, s, l in (("Cap1", (RX + 0.5, 0.3, 0.05), (RX / 2, -0.1, 0.47)),
                 ("Cap2", (0.3, RY + 0.2, 0.05), (RX + 0.1, 0.05 + (RY + 0.2) / 2, 0.47))):
    box("SM_Brick" + nm, s, l, M["midwood"])
# wainscot (dark wood panels) + baseboard + rail on both back walls
box("SM_WainscotBack", (RX, 0.05, 1.0), (RX / 2, RY - 0.025, 0.5), M["wainscot"])
box("SM_WainscotLeft", (0.05, RY - 0.05, 1.0), (0.025, (RY - 0.05) / 2, 0.5), M["wainscot"])
box("SM_RailBack", (RX, 0.08, 0.06), (RX / 2, RY - 0.04, 1.03), M["darkwood"])
box("SM_RailLeft", (0.08, RY - 0.08, 0.06), (0.04, (RY - 0.08) / 2, 1.03), M["darkwood"])
box("SM_CrownBack", (RX, 0.1, 0.1), (RX / 2, RY - 0.05, RH - 0.05), M["darkwood"])
box("SM_CrownLeft", (0.1, RY - 0.1, 0.1), (0.05, (RY - 0.1) / 2, RH - 0.05), M["darkwood"])


# ---- shelves full of archive boxes ----------------------------------------------------
def shelf_unit(tag, axis, c, width, depth=0.45, height=2.45, rows=5):
    """axis 'X': runs along the back wall (y=RY). axis 'Y': along the left wall (x=0)."""
    def place(u, d_off, z, sx, sd, sz, mat, nm):
        if axis == "X":
            return box(nm, (sx, sd, sz), (c + u, RY - d_off, z), mat)
        return box(nm, (sd, sx, sz), (d_off, c + u, z), mat)
    h = width / 2
    place(-h + 0.02, depth / 2, height / 2, 0.04, depth, height, M["darkwood"], f"SM_{tag}_SideA")
    place(h - 0.02, depth / 2, height / 2, 0.04, depth, height, M["darkwood"], f"SM_{tag}_SideB")
    place(0, depth / 2, height + 0.02, width + 0.06, depth, 0.05, M["darkwood"], f"SM_{tag}_Top")
    place(0, depth / 2, 0.05, width, depth, 0.1, M["darkwood"], f"SM_{tag}_Base")
    gap = (height - 0.15) / rows
    for r in range(rows):
        z0 = 0.1 + r * gap
        place(0, depth / 2, z0, width, depth, 0.03, M["midwood"], f"SM_{tag}_Plank{r}")
        u = -h + 0.07
        while u < h - 0.14:
            w = random.choice([0.12, 0.16, 0.2, 0.26, 0.32])
            bh = gap * random.choice([0.62, 0.7, 0.78, 0.84])
            if u + w > h - 0.06:
                break
            if random.random() < 0.08:          # a gap on the shelf
                u += 0.2
                continue
            place(u + w / 2, depth * 0.52, z0 + 0.015 + bh / 2, w * 0.96, depth * 0.62, bh,
                  random.choice(BOXES), f"SM_{tag}_Box")
            u += w + 0.012


shelf_unit("ShelfBack", "X", 1.5, 2.6)
shelf_unit("ShelfLeft", "Y", 1.9, 2.6)

# ---- door on the back wall (right side), "CASE FILES" sign ---------------------------------
DX = 4.7
box("SM_DoorFrame", (1.2, 0.07, 2.3), (DX, RY - 0.035, 1.15), M["darkwood"])
box("SM_DoorLeaf", (0.98, 0.06, 2.12), (DX, RY - 0.075, 1.06), M["midwood"])
box("SM_DoorPanelA", (0.7, 0.03, 0.75), (DX, RY - 0.11, 1.5), M["darkwood"])
box("SM_DoorPanelB", (0.7, 0.03, 0.75), (DX, RY - 0.11, 0.65), M["darkwood"])
ball("SM_DoorKnob", 0.04, (DX + 0.36, RY - 0.13, 1.0), M["gold"])
box("SM_DoorStep", (1.3, 0.25, 0.08), (DX, RY - 0.12, 0.04), M["midwood"])
txt = bpy.data.curves.new("SignText", "FONT")
txt.body = "CASE FILES"
txt.align_x = "CENTER"
txt.size = 0.2
txt.extrude = 0.01
sign = bpy.data.objects.new("SM_Sign", txt)
sign.location = (DX, RY - 0.12, 2.42)
sign.rotation_euler = (math.pi / 2, 0, 0)
col.objects.link(sign)
sign.data.materials.append(M["sign"])
box("SM_SignBoard", (1.5, 0.04, 0.34), (DX, RY - 0.06, 2.42), M["darkwood"])

# ---- window on the left wall --------------------------------------------------------------
WY = 4.15
box("SM_WinFrame", (0.08, 1.2, 1.5), (0.04, WY, 1.7), M["darkwood"])
box("SM_WinGlass", (0.02, 1.04, 1.34), (0.085, WY, 1.7), M["window"], bevel=0.0)
box("SM_WinMullionV", (0.05, 0.04, 1.34), (0.1, WY, 1.7), M["darkwood"])
box("SM_WinMullionH", (0.05, 1.04, 0.04), (0.1, WY, 1.7), M["darkwood"])
box("SM_WinSill", (0.2, 1.35, 0.05), (0.1, WY, 0.94), M["midwood"])

# ---- notice board (back wall), frames, wall lantern -----------------------------------------
box("SM_NoticeBoard", (1.1, 0.04, 0.8), (3.15, RY - 0.03, 1.75), M["cork"])
box("SM_NoticeFrame", (1.2, 0.03, 0.9), (3.15, RY - 0.012, 1.75), M["darkwood"])
for i in range(7):
    box("SM_Pin", (0.18, 0.005, 0.24), (2.75 + random.random() * 0.8, RY - 0.06, 1.5 + random.random() * 0.5),
        M["paper"], rot=(0, 0, 0), bevel=0.0)
for i, (y, z, w, h) in enumerate(((0.55, 2.0, 0.04, 0.5), )):
    pass
box("SM_FrameA", (0.04, 0.5, 0.38), (0.03, 0.55, 1.95), M["darkwood"])
box("SM_FrameAArt", (0.02, 0.42, 0.3), (0.055, 0.55, 1.95), M["window"])
LANT = (0.12, 3.4, 1.9)
box("SM_LanternArm", (0.14, 0.03, 0.03), (0.07, 3.4, 2.0), M["metal"])
box("SM_LanternBody", (0.12, 0.12, 0.2), LANT, M["lantern"])
box("SM_LanternCap", (0.16, 0.16, 0.04), (0.12, 3.4, 2.03), M["metal"])

# ---- rug, desk, chair, items -----------------------------------------------------------------
DXc, DYc = 3.3, 2.3
box("SM_RugEdge", (3.0, 2.2, 0.012), (DXc, DYc + 0.2, 0.006), M["rugedge"], bevel=0.003)
box("SM_Rug", (2.8, 2.0, 0.016), (DXc, DYc + 0.2, 0.01), M["rug"], bevel=0.003)
box("SM_DeskTop", (1.9, 0.95, 0.08), (DXc, DYc, 0.76), M["midwood"])
box("SM_DeskApron", (1.7, 0.75, 0.1), (DXc, DYc, 0.68), M["darkwood"])
for sx in (-0.85, 0.85):
    for sy in (-0.4, 0.4):
        box("SM_DeskLeg", (0.08, 0.08, 0.72), (DXc + sx, DYc + sy, 0.36), M["darkwood"])
box("SM_DeskDrawers", (0.5, 0.8, 0.45), (DXc + 0.6, DYc, 0.45), M["darkwood"])
for dz in (0.34, 0.5):
    ball("SM_DrawerKnob", 0.018, (DXc + 0.6, DYc - 0.41, dz), M["gold"])
# lamp
LAMP = (DXc - 0.55, DYc + 0.2, 0.8)
cyl("SM_LampBase", 0.09, 0.07, 0.04, (LAMP[0], LAMP[1], 0.82), M["metal"])
cyl("SM_LampPost", 0.012, 0.012, 0.4, (LAMP[0], LAMP[1], 1.02), M["metal"])
cyl("SM_LampShade", 0.05, 0.16, 0.14, (LAMP[0] + 0.08, LAMP[1], 1.3), M["green"], rot=(0, math.radians(18), 0))
ball("SM_LampBulb", 0.045, (LAMP[0] + 0.08, LAMP[1], 1.24), M["bulb"])
# papers, books, folder, mug
for i, (dx, dy, rz) in enumerate(((-0.1, 0.0, 0.2), (0.25, -0.05, -0.15), (0.05, -0.25, 0.4))):
    box("SM_Paper", (0.3, 0.4, 0.004), (DXc + dx, DYc + dy, 0.805 + i * 0.004), M["paper"], rot=(0, 0, rz), bevel=0.0)
for i, mat in enumerate(BOOKS):
    box("SM_Book", (0.3 - i * 0.02, 0.22, 0.05), (DXc + 0.65, DYc + 0.25, 0.825 + i * 0.05), mat,
        rot=(0, 0, 0.12 * i - 0.1))
box("SM_Folder", (0.26, 0.34, 0.02), (DXc + 0.38, DYc - 0.15, 0.81), M["midwood"], rot=(0, 0, -0.3), bevel=0.003)
cyl("SM_Mug", 0.04, 0.04, 0.09, (DXc - 0.3, DYc - 0.25, 0.845), M["pot"])
# chair
CY = DYc + 1.0
box("SM_ChairSeat", (0.5, 0.5, 0.06), (DXc, CY, 0.46), M["midwood"], rot=(0, 0, 0.1))
box("SM_ChairBack", (0.5, 0.05, 0.55), (DXc - 0.03, CY + 0.25, 0.8), M["darkwood"], rot=(0, 0, 0.1))
for sx in (-0.2, 0.2):
    for sy in (-0.2, 0.2):
        box("SM_ChairLeg", (0.05, 0.05, 0.44), (DXc + sx, CY + sy, 0.22), M["darkwood"])

# ---- filing cabinet, crates, plant ---------------------------------------------------------------
box("SM_Cabinet", (0.55, 0.6, 1.3), (5.6, 3.15, 0.65), M["metal"])
for dz in (0.25, 0.65, 1.05):
    box("SM_CabinetDrawer", (0.02, 0.5, 0.3), (5.6 - 0.285, 3.15, dz), M["darkwood"])
    box("SM_CabinetHandle", (0.02, 0.14, 0.03), (5.6 - 0.3, 3.15, dz + 0.05), M["gold"], bevel=0.0)
for i, (x, y, z, s, r) in enumerate(((0.8, 0.8, 0.2, 0.4, 0.2), (1.35, 0.7, 0.18, 0.36, -0.3), (1.0, 0.85, 0.6, 0.34, 0.5))):
    box("SM_Crate", (s, s * 1.15, s * 0.9), (x, y, z + 0.0), M["midwood"], rot=(0, 0, r))
cyl("SM_Pot", 0.22, 0.16, 0.34, (5.4, 4.35, 0.17), M["pot"])
for i in range(9):
    a = i * 0.7
    ball("SM_Leaf", 0.1, (5.4 + 0.18 * math.cos(a), 4.35 + 0.18 * math.sin(a), 0.62 + 0.07 * (i % 3)),
         M["leaf"], scale=(1, 0.4, 2.6), rot=(0, 0.5 * ((i % 3) - 1), a))

# ---- pixel hero billboard (HD-2D: pixel actor on a 3D stage) -----------------------------------
img_path = os.path.normpath(SPRITE)
if CHAR_MODE == "sprite" and os.path.isfile(img_path):
    full = bpy.data.images.load(img_path, check_existing=True)
    w, h = full.size
    px = list(full.pixels)
    fw = w // 3
    fh = h // 4
    # row 0 of the sheet (down), frame 0 (idle). Image rows are stored bottom-up.
    y0 = h - fh
    out = []
    for y in range(fh):
        row = (y0 + y) * w * 4
        out.extend(px[row: row + fw * 4])
    sprite = bpy.data.images.new("hero_idle_down", fw, fh, alpha=True)
    sprite.pixels = out
    sprite.pack()
    ms = new_mat("M_HeroSprite")
    nt = ms.node_tree
    b = principled(ms)
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = sprite
    tex.interpolation = "Closest"
    nt.links.new(tex.outputs["Color"], b.inputs["Base Color"])
    nt.links.new(tex.outputs["Alpha"], b.inputs["Alpha"])
    nt.links.new(tex.outputs["Color"], b.inputs["Emission Color"])
    set_in(b, "Emission Strength", 0.35)
    set_in(b, "Roughness", 1.0)
    try:
        ms.surface_render_method = "DITHERED"
    except Exception:
        pass
    bq = bmesh.new()
    v = [bq.verts.new(p) for p in ((-0.85, 0, 0), (0.85, 0, 0), (0.85, 0, 1.7), (-0.85, 0, 1.7))]
    f = bq.faces.new(v)
    uvl = bq.loops.layers.uv.new("UVMap")
    for lp, uvp in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))):
        lp[uvl].uv = uvp
    me = bpy.data.meshes.new("SM_HeroSprite")
    bq.to_mesh(me)
    bq.free()
    hero = bpy.data.objects.new("SM_HeroSprite", me)
    hero.location = (2.35, 1.35, 0.015)
    hero.rotation_euler = (0, 0, math.radians(45))
    col.objects.link(hero)
    hero.data.materials.append(ms)


# ---- 3D characters (same art style as the room): body mesh + separate clothes -----------------
def build_characters():
    ns = runpy.run_path(os.path.join(HERE, "..", "male_base.py"))      # builds SM_MaleBase
    src = bpy.data.objects["SM_MaleBase"]
    base = src.data.copy()
    mc = bpy.data.collections.get("MaleBase")
    for o in list(mc.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    bpy.data.collections.remove(mc)
    # relax the A-pose: swing both arms in toward the body (smooth, shoulder stays put)
    side_pivot = 0.215
    for v in base.vertices:
        s_ = 1 if v.co.x > 0 else -1
        if abs(v.co.x) > 0.19 and 0.7 < v.co.z < 1.5:
            dx, dz = (abs(v.co.x) - side_pivot), v.co.z - 1.452
            r = math.hypot(dx, dz)
            if dz < 0.05 and r > 0.06:
                w = min(1.0, (r - 0.06) / 0.14)
                phi = math.atan2(dx, -dz) - math.radians(21) * w
                v.co.x = s_ * (side_pivot + r * math.sin(phi))
                v.co.z = 1.452 - r * math.cos(phi)
    base.update()

    def mk(name, color, rough=0.8):
        return flat(name, color, rough)

    def garment(parent, name, cond, off, thick, mat):
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
        ob.parent = parent
        ob.data.materials.append(mat)
        sm = ob.modifiers.new("Thickness", "SOLIDIFY")
        sm.thickness = thick
        sm.offset = 1.0
        try:
            me.shade_smooth()
        except AttributeError:
            pass
        return ob

    def part(parent, name, kind, loc, size, mat, rot=(0, 0, 0)):
        if kind == "ball":
            b = bmesh.new()
            bmesh.ops.create_uvsphere(b, u_segments=18, v_segments=10, radius=1.0,
                                      matrix=Matrix.Diagonal((*size, 1.0)))
        elif kind == "cone":
            b = bmesh.new()
            bmesh.ops.create_cone(b, cap_ends=True, segments=28, radius1=size[0], radius2=size[1], depth=size[2])
        else:
            b = bmesh.new()
            bmesh.ops.create_cube(b, size=1.0, matrix=Matrix.Diagonal((*size, 1.0)))
        me = bpy.data.meshes.new(name)
        b.to_mesh(me)
        b.free()
        ob = bpy.data.objects.new(name, me)
        ob.parent = parent
        ob.location = loc
        ob.rotation_euler = rot
        col.objects.link(ob)
        ob.data.materials.append(mat)
        if kind != "cube":
            try:
                me.shade_smooth()
            except AttributeError:
                pass
        return ob

    def person(tag, loc, rz, scale, skin, hair, outfit):
        body = bpy.data.objects.new(f"SM_{tag}_Body", base.copy())
        body.location = loc
        body.rotation_euler = (0, 0, rz)
        body.scale = (scale, scale, scale)
        col.objects.link(body)
        body.data.materials.append(mk(f"M_{tag}_Skin", skin, 0.6))
        torso = lambda c: abs(c.x) < 0.19 and 0.93 < c.z < 1.46
        arms = lambda c: abs(c.x) > 0.19 and 0.93 < c.z < 1.5
        legs = lambda c: 0.14 < c.z <= 0.93
        feet = lambda c: c.z <= 0.14
        garment(body, f"SM_{tag}_Boots", feet, 0.006, 0.01, mk(f"M_{tag}_Boots", (0.13, 0.08, 0.05), 0.6))
        garment(body, f"SM_{tag}_Trousers", legs, 0.007, 0.012, mk(f"M_{tag}_Trousers", outfit["pants"]))
        if outfit["kind"] == "coat":
            garment(body, f"SM_{tag}_Coat", lambda c: torso(c) or arms(c), 0.012, 0.014,
                    mk(f"M_{tag}_Coat", outfit["top"], 0.9))
            part(body, f"SM_{tag}_CoatSkirt", "cone", (0, 0.005, 0.78), (0.19, 0.25, 0.34),
                 mk(f"M_{tag}_CoatSkirtM", outfit["top"], 0.9)).scale = (1.0, 0.62, 1.0)
            part(body, f"SM_{tag}_Satchel", "cube", (0.26, 0.0, 0.86), (0.08, 0.30, 0.24), mk(f"M_{tag}_Bag", (0.38, 0.22, 0.10), 0.7))
            part(body, f"SM_{tag}_Strap", "cube", (0.0, -0.005, 1.17), (0.03, 0.34, 0.62),
                 mk(f"M_{tag}_StrapM", (0.30, 0.17, 0.08), 0.7), rot=(0, 0.42, 0))
        else:
            garment(body, f"SM_{tag}_Shirt", arms, 0.01, 0.01, mk(f"M_{tag}_Shirt", (0.86, 0.82, 0.72), 0.85))
            garment(body, f"SM_{tag}_Vest", torso, 0.016, 0.014, mk(f"M_{tag}_Vest", outfit["top"], 0.8))
            part(body, f"SM_{tag}_Belt", "cube", (0.0, 0.0, 0.94), (0.40, 0.25, 0.05), mk(f"M_{tag}_BeltM", (0.30, 0.17, 0.08), 0.6))
        hair_m = mk(f"M_{tag}_Hair", hair, 0.5)
        part(body, f"SM_{tag}_Hair", "ball", (0.0, 0.012, 1.745), (0.104, 0.112, 0.085), hair_m)
        part(body, f"SM_{tag}_HairBack", "ball", (0.0, 0.05, 1.70), (0.09, 0.07, 0.09), hair_m)
        if outfit["kind"] != "coat":                                  # ponytail
            part(body, f"SM_{tag}_Ponytail", "ball", (0.0, 0.12, 1.66), (0.05, 0.06, 0.12), hair_m, rot=(0.35, 0, 0))
        return body

    man = person("Man", (2.25, 0.95, 0.0), math.radians(180 - 12), 0.98, (0.55, 0.36, 0.26), (0.05, 0.035, 0.03),
                 {"kind": "coat", "top": (0.07, 0.07, 0.09), "pants": (0.05, 0.05, 0.07)})
    wom = person("Woman", (3.3, 0.95, 0.0), math.radians(180 + 22), 0.9, (0.86, 0.66, 0.55), (0.52, 0.21, 0.10),
                 {"kind": "vest", "top": (0.07, 0.26, 0.2), "pants": (0.42, 0.34, 0.2)})
    return man, wom


if CHAR_MODE == "3d":
    build_characters()

# ---- lights ----------------------------------------------------------------------------------------
light("LGT_DeskLamp", "POINT", (LAMP[0] + 0.1, LAMP[1], 1.22), (1.0, 0.62, 0.28), 260, 0.12)
light("LGT_Lantern", "POINT", (0.28, 3.4, 1.9), (1.0, 0.58, 0.22), 90, 0.08)
light("LGT_Window", "AREA", (0.35, WY, 1.7), (0.5, 0.65, 1.0), 170, 1.3, rot=(0, -math.pi / 2, 0))
light("LGT_Fill", "AREA", (8.5, -5.5, 6.5), (0.75, 0.78, 1.0), 260, 5.0,
      rot=(math.radians(52), 0, math.radians(45)))
light("LGT_Warm", "AREA", (3.2, 2.4, 3.6), (1.0, 0.72, 0.45), 110, 3.0)

# ---- camera: true isometric, orthographic ---------------------------------------------------------
target = Vector((3.0, 2.3, 1.0))
direction = Vector((-1, 1, -math.sqrt(2) / 1.0 * 0.5 * math.sqrt(2))).normalized()  # (-1, 1, -1)
cam = bpy.data.objects.new("CAM_Iso_Office", bpy.data.cameras.new("CAM_Iso_Office"))
cam.data.type = "ORTHO"
cam.data.ortho_scale = 9.2
cam.data.clip_end = 100
cam.location = target - direction * 22
cam.rotation_euler = (math.radians(54.7356), 0, math.radians(45))
col.objects.link(cam)
bpy.context.scene.camera = cam

# ---- world: dark cool ambience -----------------------------------------------------------------------
sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new("World")
w = sc.world
if not w.node_tree:
    w.use_nodes = True
bg = next(n for n in w.node_tree.nodes if n.type == "BACKGROUND")
bg.inputs["Color"].default_value = (0.045, 0.035, 0.035, 1)
bg.inputs["Strength"].default_value = 1.0
print("Hero Office built:", len(col.objects), "objects")
