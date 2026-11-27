"""Anime / cel-shaded look for the MHA RPG (anime-style skill).

Run inside Blender AFTER male_base.py (Scripting tab -> New -> paste -> Run).
Adds, without changing the body's shape:
  - a cel shader: 3 flat value steps (shadow / base / light), hard edges
  - a thick ink outline (inverted hull: Solidify with flipped normals)
Switch the viewport to Material Preview or Rendered with EEVEE to see it.
Safe to re-run. To remove: delete the "InkOutline" modifier and the toon
material slots from SM_MaleBase.
"""
import bpy

TARGET = "SM_MaleBase"
OUTLINE = 0.004          # ink line thickness in metres

ob = bpy.data.objects.get(TARGET)
if ob is None:
    raise SystemExit(f"No {TARGET!r}. Run male_base.py first.")


def fresh(name):
    m = bpy.data.materials.get(name)
    if m:
        bpy.data.materials.remove(m)
    m = bpy.data.materials.new(name)
    if not m.node_tree:
        m.use_nodes = True
    m.node_tree.nodes.clear()
    return m


# ---- cel shader: Diffuse -> Shader to RGB -> constant ramp -> Emission ------------
toon = fresh("M_Toon_Skin")
nt = toon.node_tree
out = nt.nodes.new("ShaderNodeOutputMaterial")
dif = nt.nodes.new("ShaderNodeBsdfDiffuse")
s2r = nt.nodes.new("ShaderNodeShaderToRGB")
ramp = nt.nodes.new("ShaderNodeValToRGB")
emit = nt.nodes.new("ShaderNodeEmission")
cr = ramp.color_ramp
cr.interpolation = "CONSTANT"
cr.elements[0].position = 0.0
cr.elements[0].color = (0.20, 0.15, 0.13, 1)       # shadow
cr.elements[1].position = 0.30
cr.elements[1].color = (0.42, 0.34, 0.29, 1)       # base
hi = cr.elements.new(0.80)
hi.color = (0.58, 0.49, 0.43, 1)                    # light
nt.links.new(dif.outputs["BSDF"], s2r.inputs["Shader"])
nt.links.new(s2r.outputs["Color"], ramp.inputs["Fac"])
nt.links.new(ramp.outputs["Color"], emit.inputs["Color"])
nt.links.new(emit.outputs["Emission"], out.inputs["Surface"])

# ---- ink outline material: black, back faces only ------------------------------------
ink = fresh("M_Toon_Ink")
nt = ink.node_tree
o2 = nt.nodes.new("ShaderNodeOutputMaterial")
e2 = nt.nodes.new("ShaderNodeEmission")
e2.inputs["Color"].default_value = (0.01, 0.01, 0.012, 1)
nt.links.new(e2.outputs["Emission"], o2.inputs["Surface"])
ink.use_backface_culling = True

# ---- assign: slot 0 toon skin, slot 1 ink ----------------------------------------------
ob.data.materials.clear()
ob.data.materials.append(toon)
ob.data.materials.append(ink)
for p in ob.data.polygons:
    p.material_index = 0

for m in [m for m in ob.modifiers if m.name == "InkOutline"]:
    ob.modifiers.remove(m)
sol = ob.modifiers.new("InkOutline", "SOLIDIFY")
sol.thickness = OUTLINE
sol.offset = 1.0
sol.use_flip_normals = True
sol.use_rim = False
sol.material_offset = 1

print("Toon look applied: 3-step cel shader + ink outline on", TARGET)
print("Tip: viewport shading -> Rendered, render engine EEVEE.")
