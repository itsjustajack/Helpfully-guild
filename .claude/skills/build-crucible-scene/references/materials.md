# Materials: colour, patterns, glass, water, shader hooks

<!-- skill-navigation:start -->
This is the [Materials: colour, patterns, glass, water, shader hooks](#materials-colour-patterns-glass-water-shader-hooks) reference. Read [Colour and values](#colour-and-values) and [Patterns](#patterns) before texturing a part.
Then read the task's section: [Glass, coat, sheen and wax](#glass-coat-sheen-and-wax), [Water and sea](#water-and-sea), [Shader hooks](#shader-hooks),
[Editing materials and imports](#editing-materials-and-imports) or [Judge a surface](#judge-a-surface).
<!-- skill-navigation:end -->

Calls follow the conventions in `look.md`. `tests/skill-examples.test.js` applies every block, so they stay valid.
Field lists and ranges: `scene_capabilities` topics `materialFields`, `materialLayers`, `pattern`, `materialSnippet`.
Blocky parts that carry a material name (Roblox-style): set `preset` (`smoothPlastic`, `wood`, `grass`, `glass`, `brick`) and `color`; the colour tints the preset and any field you set wins. Topic `materialPresets`.

## Colour and values

| Field | Range | Note |
|---|---|---|
| `color` | each channel 0 to 1, linear | Hue only; brightness comes from light. |
| `metallic`, `roughness` | 0 to 1 | The renderer keeps a roughness floor of 0.075. |
| `emission` | 0 or more | A multiplier. `emissiveColor` is its own linear RGB, each channel 0 or more. |
| `opacity` | 0 to 1 | Below 1 on an opaque material turns it into `blend`. |
| `alphaMode` | `opaque`, `mask`, `blend`, `add` | `mask` cuts out where map alpha times `opacity` is below `alphaCutoff` (`0.5` default); `add` adds its light to what is behind it (sparks, beams). |
| `alphaCutoff` | 0 to 1 (default `0.5`) | Used only with `alphaMode: "mask"`; rejects other alpha modes. |
| `doubleSided` | `true` or `false` | Thin sheets, leaves, cards. |

Starting values, then judge with `scene_look`:

| Kind | `color` | `metallic` | `roughness` |
|---|---|---|---|
| Rough stone, plaster | mid grey, or white under a pattern | 0 | 0.85 to 1 |
| Painted wall, car paint | the hue | 0 | 0.3 to 0.6 (add `clearcoat` for a gloss) |
| Bare metal | light grey or the metal tint | 1 | 0.2 to 0.5 |
| Rubber, cloth | dark | 0 | 0.9 |
| Lamp, screen | the hue | 0 | any, with `emission` 2 to 8 |

Metal is 0 or 1 in practice; use a value between only for a worn edge. A smooth metal part adds automatic reflection probes, and a scene over
200000 triangles used to fail `scene_apply` with "Light bake takes at most 200000 triangles" although no bake was asked for. Since #2202 the
probes are skipped past that limit and the sky reflection stays, so `metallic` above 0 is safe; the skip reason names `environment.objectReflections`.

## Patterns

Colour multiplies the pattern's own colours. A dark `color` on a dark stone pattern renders near black, so keep
`color: [1, 1, 1]` on a patterned material and change the look through the pattern's `colors`. Roughness and metallic
also multiply the pattern's maps: `roughness: 1` keeps the pattern's own roughness.

```json
{ "expectedRevision": 1, "operations": [
  { "type": "add-material", "material": { "id": "rock", "color": [1, 1, 1], "roughness": 1,
    "pattern": { "type": "stone", "size": 1.5, "count": 4, "bump": 1.2, "seed": 7 } } },
  { "type": "set-node", "id": "body", "material": "rock" }
] }
```

- `type`: `noise`, `wood`, `planks`, `bricks`, `tiles`, `marble`, `stone`, `concrete`, `metal`, `rust`, `fabric`, or `graph` (your own node graph; see `scene_capabilities` `materialGraph`).
- `size` is metres per repeat (0.01 to 100), so the grain keeps its real size on any node scale. `count` (1 to 64) is rings, planks, bricks or cells per repeat. `bump` is relief, 0 to 4. `seed` varies it.
- `axis` (`x`, `y`, `z`, default `y`) is the object axis wood, planks and brushed metal run along. `mapping` is `box` (default, no UVs needed) or `uv`.
- `colors` is two linear RGB colours, darker first. Only `bricks` takes a third (the mortar); a third colour on any other type fails with "Material pattern colors must be two linear RGB colours ... (three for bricks ...)".
- `resolution` is 256, 512 (default, about 4 MiB a pattern) or 1024.
- A scene holds at most 16 different patterns. Two materials with identical pattern JSON count once, so reuse one pattern and tint it with `color`.
- A pattern needs the `surface` tag. On any other tag (`water`, `liquid`, `foam`, `unlit`, `foliage`, `grass`) it fails; keep the `surface` tag or remove the pattern.

```json
{ "expectedRevision": 1, "operations": [
  { "type": "add-material", "material": { "id": "wall", "color": [1, 1, 1], "roughness": 0.95,
    "pattern": { "type": "bricks", "colors": [[0.33, 0.1, 0.06], [0.52, 0.2, 0.12], [0.45, 0.42, 0.38]], "count": 6, "size": 1.2 } } },
  { "type": "set-node", "id": "body", "material": "wall" }
] }
```

## Glass, coat, sheen and wax

Layer fields and ranges (`scene_capabilities` `materialLayers`): `clearcoat` 0 to 1, `clearcoatRoughness` 0 to 1, `transmission` 0 to 1,
`thickness` 0 to 1000 m, `ior` 1 to 2.5, `specular` 0 to 4, `sheenColor` and `attenuationColor` 0 to 1 per channel, `sheenRoughness` 0 to 1,
`anisotropy` 0 to 1, `iridescence` 0 to 1, `attenuationDistance` above 0.

- Glass: `transmission: 1` with a nonzero `thickness`. With `thickness: 0` the view is not bent. Leave `opacity: 1` and `alphaMode: "opaque"`: a transmitting material that is also blended does not refract, and `scene_inspect` says so (`transmission-blended`).
- Transmission needs the `surface` or `liquid` tag. It ignores `anisotropy` and `iridescence`, and `thickness`, `attenuationColor` and `attenuationDistance` do nothing while `transmission` is 0. A window pane also takes `rayVisibility: 'glass'` (see `SKILL.md`).
- `clearcoat`, `sheenColor`, `specular`, `specularColor`, `anisotropy` and `iridescence` apply only to the `surface` and `liquid` tags; other tags raise an `ignored-material-field` diagnostic.
- `subsurface` (skin, wax, leaves): `weight` 0 to 1, `radius` [r, g, b] 0 to 100, `scale` 0 to 10 metres per radius unit, `color` 0 to 1. Surface tag, rasterizer only.

```json
{ "expectedRevision": 1, "operations": [
  { "type": "add-material", "material": { "id": "glass", "color": [1, 1, 1], "roughness": 0.05, "transmission": 1, "thickness": 0.04, "ior": 1.5,
    "attenuationColor": [0.8, 0.95, 0.9], "attenuationDistance": 2 } },
  { "type": "add-material", "material": { "id": "lacquer", "color": [0.6, 0.05, 0.04], "roughness": 0.4, "clearcoat": 1, "clearcoatRoughness": 0.05 } },
  { "type": "add-material", "material": { "id": "wax", "color": [0.9, 0.8, 0.6], "roughness": 0.5,
    "subsurface": { "weight": 0.6, "radius": [1, 0.4, 0.2], "scale": 0.05, "color": [0.9, 0.7, 0.5] } } },
  { "type": "set-node", "id": "body", "material": "glass" },
  { "type": "set-node", "id": "lid", "material": "lacquer" }
] }
```

## Water and sea

Tags (`tag` on `add-material`): `surface` (default), `unlit`, `liquid`, `foam`, `foliage`, `grass`, `water`. A `water` material takes
`waterPreset` (`lake`, `sea`, `river`), `absorption` (RGB per metre, 0 to 20), `turbidity` (0 clear to 1 murky) and an optional `waterRamp`;
an `opacity` under 1 shows the bed. The sea itself is an `ocean` mesh edit; it writes the `foam` vertex group.

```json
{ "expectedRevision": 1, "operations": [
  { "type": "add-material", "material": { "id": "sea", "tag": "water", "waterPreset": "sea", "color": [0.1, 0.3, 0.45], "roughness": 0.1, "opacity": 0.9 } },
  { "type": "add-geometry", "geometry": { "id": "sea", "type": "mesh", "base": { "type": "box", "bevel": 0 },
    "edits": [ { "op": "subdivide", "levels": 4 }, { "op": "ocean", "windSpeed": 8, "choppiness": 1, "size": 20, "seed": 3 } ] } },
  { "type": "add-node", "node": { "id": "water", "geometry": "sea", "material": "sea", "scale": [20, 1, 20] } }
] }
```

`windSpeed` (0 to 60 m/s) only shapes the waves: no force pushes a prop along. Props ride the wave height through
`physics.ocean` and `float`; a boat adds `float.boat` thrust and a `wake` (docs/physics.md "Floating on the ocean"). A small prop on a
`windSpeed` 12 sea bobs hard, so lower `windSpeed` or add float points. Foam, spray and wake drive particles: see `particles-and-vfx.md`.

## Shader hooks

`snippet` is a GLSL ES 3.00 function that changes colour and alpha per fragment, or discards it. Rasterizer only; at most 4096 bytes of
code, 16 uniforms, no `#` lines, counted loops only. The engine declares your `uniforms`; do not redeclare them. Inputs: `color`, `alpha`,
`uv`, `worldPosition`. `discard` removes the fragment in every alpha mode and also removes its shadow; a lowered `alpha` fades a `blend` or `add`
part (an opaque part has nothing to fade). `snippet: null` clears it. A compile error comes back as `renderError` with snippet line numbers.

A wet band that darkens the lower half metre of a wall:

```json
{ "expectedRevision": 1, "operations": [
  { "type": "add-material", "material": { "id": "wet", "color": [0.7, 0.68, 0.64], "roughness": 0.9,
    "snippet": { "fragment": "void materialHook(inout vec3 color, inout float alpha, vec2 uv, vec3 worldPosition) {\n  float wet = 1.0 - smoothstep(bandTop - 0.2, bandTop, worldPosition.y);\n  color *= 1.0 - 0.55 * wet;\n}", "uniforms": { "bandTop": 0.5 } } } },
  { "type": "set-node", "id": "body", "material": "wet" }
] }
```

A dissolve cuts stripes with `discard`; a soft beam shell fades `alpha` along height on an additive material:

```json
{ "expectedRevision": 1, "operations": [
  { "type": "add-material", "material": { "id": "dissolve", "color": [0.8, 0.5, 0.3], "doubleSided": true,
    "snippet": { "fragment": "void materialHook(inout vec3 color, inout float alpha, vec2 uv, vec3 worldPosition) {\n  if (fract(worldPosition.y * 9.0 + worldPosition.x * 3.0) < cut) discard;\n}", "uniforms": { "cut": 0.35 } } } },
  { "type": "add-material", "material": { "id": "beam", "tag": "unlit", "color": [1, 0.9, 0.7], "alphaMode": "add", "opacity": 0.25, "doubleSided": true,
    "snippet": { "fragment": "void materialHook(inout vec3 color, inout float alpha, vec2 uv, vec3 worldPosition) {\n  alpha *= smoothstep(lowY, highY, worldPosition.y);\n}", "uniforms": { "lowY": 0.0, "highY": 3.0 } } } },
  { "type": "set-node", "id": "body", "material": "dissolve" },
  { "type": "set-node", "id": "lid", "material": "beam" }
] }
```

A single cone seen from the side shows a hard silhouette. Stack two or three shells of growing radius with falling `opacity` and
fade each along the beam. Point and spot lights also scatter in `volumeFog` (up to 8 lights, no shadows); see `particles-and-vfx.md` for fog limits.

## Editing materials and imports

- `set-material` takes colour, `metallic`, `roughness`, `emission`, `emissiveColor`, `opacity`, `alphaMode`, `alphaCutoff`, `doubleSided`, `pattern`, `map`, `subsurface`, `snippet`, water fields and the layer fields. It rejects `tag` (the error lists the fields it takes). To change a tag, `add-material` a new one and `set-node` onto it.
- A textured import (GLB placement): the `asset.materials` override multiplies its `color` into the texture, it does not replace the texture. To recolour, tint with `color` (a dark texture stays dark), or flatten with `asset.flatten.color`, which paints every material of the placement one colour and drops the textures; a named override still wins.
- Flush faces are ranked automatically, so a flicker needs no fix. To choose which of two flush nodes wins (a sticker on a surface), set `decal: true` on the top one, or `depthLayer` 1 to 4 to stack several (see `light.md`).

## Judge a surface

Light a material neutrally before judging it. `environment.setup: "overcast"` is a grey sky with no coloured panel, so hue and roughness
read honestly. `studio` has three light panels and shows gloss and metal reflections. Then turn the key light: a surface that
looks right under one light and flat or noisy under another is wrong. Apply two variants as branches and compare them in one
`scene_review` with a `branch` per shot (a variant is one `set-environment` that rotates `lightDirection` by 90 degrees about up):

```json
{ "expectedRevision": 1, "branch": "key-a", "operations": [
  { "type": "set-environment", "environment": { "setup": "overcast", "lightDirection": [-3, 6, 4] } }
] }
```

```json
{ "expectedRevision": 1, "branch": "key-b", "operations": [
  { "type": "set-environment", "environment": { "setup": "overcast", "lightDirection": [4, 6, 3] } }
] }
```

Both blocks are `scene_apply` arguments. Then `scene_review` with `shots: [{ "branch": "key-a" }, { "branch": "key-b" }]`, and keep one with `scene_restore` and its `branch`.
