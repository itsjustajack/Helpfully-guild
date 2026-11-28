# Effects and feedback: explosions, retro look, vehicle damage, asking the person

<!-- skill-navigation:start -->
This is the [effects and feedback](#effects-and-feedback-explosions-retro-look-vehicle-damage-asking-the-person) reference. Read the section for the task:
[Explosion](#explosion), [Retro look](#retro-look), [Vehicle damage](#vehicle-damage), [Ask the person with pins and lasso](#ask-the-person-with-pins-and-lasso),
[Review page for a phone](#review-page-for-a-phone) or [Splat palette and dither](#splat-palette-and-dither). Field ranges are always in `scene_capabilities`.
<!-- skill-navigation:end -->

Calls follow the conventions in `look.md`. `tests/skill-examples.test.js` applies every `operations` block, so they stay valid.

## Explosion

One `add-explosion` writes the whole blast: flash, ring, a gas-sim fire and smoke volume, bloom, sparks, dust, rubble, a scorch
decal and a camera shake, all as ordinary recipe sections whose IDs start with the blast `id`. Do not build the six systems by hand.
Read `scene_capabilities` topic `explosion` first (`size` 0.5 to 100 m, `fuel` `dry` or `oily`, `sparks`, `motionBlur`).

```json
{ "expectedRevision": 1, "operations": [
  { "type": "add-explosion", "id": "blast", "center": [0, 0, 0], "size": 6, "start": 0.5, "seed": 7, "fuel": "oily", "shake": 0.4 }
] }
```

- A scene holds one grid volume and 4 particle systems; the blast uses one volume and 3 systems, so a second blast or your own grid volume fails.
- `debris: { "node": "crate" }` breaks a convex mesh into 12 thrown pieces; send `set-physics` with a fixed floor first.
- The fire grid is baked from the name when the server applies the batch (about 4 s the first time for a fuel and seed). No file is needed.
- `bakeGasSim` and `bakeGasSimToGrids` (`docs/volumetric.md`) are library functions, not MCP tools. Over MCP the gas sim comes only through `add-explosion`.

## Retro look

`retro` on a material gives the PlayStation 1 look in raster renders: `vertexSnap: [width, height]` (whole numbers 16 to 4096) snaps
vertices to a screen grid so they jitter with the camera, and `affineUV: true` makes textures swim on large triangles. Set either or both.
The path tracer ignores it and shadows come from the unsnapped mesh. The topic is `materialRetro`.

```json
{ "expectedRevision": 2, "operations": [
  { "type": "set-material", "id": "paint", "retro": { "vertexSnap": [160, 120], "affineUV": true } }
] }
```


## Vehicle damage

Reachable over MCP (`scene_capabilities` topic `vehicleDamage`, `docs/vehicle.md`): a `dented` geometry, which pushes `source` in around
each impact (`impacts` 1 to 8 of `{ point, direction, impulse }` in N s; `stiffness` 2000, `maxDepth` 0.25 m, `radius` 0.4 m by default),
and a part that tears off as a physics body on a `fixed` joint with `breakImpulse`. A dent keeps the vertex count and the source cannot
be a fragment or another dent.

```json
{ "expectedRevision": 3, "operations": [
  { "type": "add-geometry", "geometry": { "id": "body-dented", "type": "dented", "source": "cube", "stiffness": 40000, "maxDepth": 0.3, "radius": 0.5,
    "impacts": [ { "point": [0, 0.5, 0.5], "direction": [0, 0, -1], "impulse": 9000 } ] } },
  { "type": "set-node", "id": "body", "geometry": "body-dented" }
] }
```

Not reachable over MCP: `detachedPartFlight` (a loose part's flight in a kinematic drive, `part.size` the box extents so no corner
crosses the wall) and `hingedDoorSwing`. They are library helpers of `@codepawlhq/crucible/addons/vehicle`; no `scene_apply`
operation calls them, so do not write one. Read `docs/vehicle.md` only when you write scene code.

## Ask the person with pins and lasso

`scene_ask_user` is for a change the person cannot put in words ("warmer here", "this bit"), not for facts you can inspect. It
opens the current view in their browser (in an MCP Apps host, inline in the chat, answering `outcome: "pending"` at once). They
pin up to 16 points with a note each. A mark returns `partId`, `point`, `normal`, `note`, `distance`, `material` and `view.camera`.

- A pin or lasso carrying `materialSharedWith` (part IDs, at most 8; `materialSharedWithMore` counts the rest) means other parts use
  that material, so changing it changes them too. Give the part its own material first, then edit that one:

```json
{ "expectedRevision": 4, "operations": [
  { "type": "add-material", "material": { "id": "paint-warm", "color": [0.4, 0.6, 0.8] } },
  { "type": "set-node", "id": "lid", "material": "paint-warm" },
  { "type": "set-material", "id": "paint-warm", "color": [0.8, 0.55, 0.4] }
] }
```

- A mark with `kind: "lasso"` is an outline: apply the note to every entry of its `parts` (`partId`, `coverage`, `material`, most
  covered first). A part with `edge: true` (coverage under 0.15) only grazes the outline: skip it when the note does not fit.
  Only the browser view makes lassos; the inline chat view and the review page take pins only.
- `outcome` `cancelled` or `timeout` returns no marks: ask in plain text. Edits made while they mark change `revision`; the result warns.
- For a film scene, pass `motionTime` (0 to 3600 s): the view is seeked to that moment before they mark, the marks are resolved
  at it, and `view.motionTime` in the answer names it (left out for a scene with no motion). Without it they mark the current pose.

## Review page for a phone

`scene_export_web` with `review: true` (needs `--jobs`, no game) writes `index.html` and `frame.png` under `<jobs>/exports/`. Host
the folder or send it. The reviewer taps to pin and presses Save file or Copy. Pass the text of that file (at most 16 KiB) to
`scene_ask_user` as `reviewFile`: the marks come back with the same fields as a local call, without the PNG. Each export is read once, and
the server remembers the camera of the last 8 exports, so export again after a second read or a restart.

## Splat palette and dither

Library code, not a recipe field: `createGaussianSplats(data, { alphaCut: 0.5, palette: ['#1b1b2f', '#c8553d', '#ffd166'], dither: 'bayer4' })`
from `@codepawlhq/crucible/addons/gaussian-splats`. `palette` is 2 to 256 colours (hex strings or `[r, g, b]` of 0 to 1) and needs
`alphaCut`; `dither` is `none`, `bayer4` or `bayer8`. Only opaque splat pixels snap. `outline: { color, width }` adds a pixel outline round the silhouette:
`width` is a whole number from 1 to 4, and it needs `alphaCut`. Fills cover it, so it follows the outer edge and holes, not every disc
(`docs/gaussian-splats.md`).
