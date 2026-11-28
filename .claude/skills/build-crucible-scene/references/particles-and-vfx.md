# Particles and VFX: spray, dust, sparks, sea foam, fog and beams

<!-- skill-navigation:start -->
This is the [Particles and VFX](#particles-and-vfx-spray-dust-sparks-sea-foam-fog-and-beams) reference. Read [Caps](#caps) and [Nothing shows](#nothing-shows) before the first system.
Then read the task's section: [Spray, dust and sparks](#spray-dust-and-sparks), [Check a system](#check-a-system), [Sea spray, foam and wake](#sea-spray-foam-and-wake),
[Fog and beams](#fog-and-beams) or [Not built yet](#not-built-yet).
<!-- skill-navigation:end -->

An explosion, blast or fireball is `add-explosion` (see `effects-and-feedback.md`), never a particle system or billboard cards; particles here are only an optional extra (sparks, debris) beside one.
Calls follow the conventions in `look.md`. `tests/skill-examples.test.js` applies every block, so they stay valid.
Field list: `scene_capabilities` topic `particles`. Full contract: `docs/physics.md` "Recipe particles and hair".
The values below are starting points that validate; none was tuned by eye, so judge each with `scene_look` at a `motionTime` inside the burst.

## Caps

| Limit | Value |
|---|---|
| Systems in `particles.systems` | 4 |
| `count` per system | 1 to 2000 |
| Particles in all systems together (emitter and hair; sparks count apart) | 4000 |
| Vertices drawn in total | 100000 |
| `type: "sparks"` count, all spark systems together | 4096 |
| `lifetime` | 0.01 to 60 s (sparks 0.05 to 5 s) |

A system draws its node's geometry once per particle, so the vertex cap is the one you hit first. A default `box` is 1176 vertices, a default
`sphere` 2665 and a default `plane` 289; the error names the vertices per particle. Use `box` with `bevel: 0` (24 vertices) or a `plane`
with `segments: 1` (4 vertices, a card). `scene_inspect` returns `particles.systems[].verticesPerParticle`, `maxAlive` and `endsAt`.

Emission: `count` is how many are born in all. With `rate` (births per second) they are spread over `count / rate` seconds; without it, all are born at time 0 in
one burst. `start` (alias `delay`) is the time of the first birth. `stop` is an absolute time in seconds, not a length after `start`: it must be above
`start` and at most 3600, so `{ "start": 1.6, "stop": 0.4 }` fails with "expected an absolute scene time in seconds, above start (1.6), such as 3.6 (stop is not a duration after start)". Nothing is born at or after `stop`;
particles already born finish their life.

`emitter.shape` is `point` (default), `box`, `sphere`, `disc` or `mesh`; `emitter.position` is in world metres. `direction` (default up) and `spread` (cone angle in degrees, 0 to 180, default 30) aim the launch.
A box emitter takes `halfExtents`, not `radius`. Crucible no longer writes a `radius` into a box emitter, and a stored `radius: 0.5` on a box is dropped, so later batches apply (#2203). `sphere` and `disc` take `radius`.

`set-particles` may name a node added in an earlier batch (#2204); the node and the system can be in one batch or two. A system replaces its node's own geometry with the
particles, so use a node made for it, and give the emitter place through `emitter.position`: the node's `translation`, `rotation` and `scale` are ignored (`scene_inspect` warns with `particle-node-transform-ignored`).

## Nothing shows

A system can validate and draw nothing. Check these before changing values:

1. The time. A system with `start: 1.6` has no particle at the default `scene_look` time; pass `motionTime` between `start` and `endsAt` from the report.
2. The card. A `plane` faces +Z and keeps its facing, so seen from the side it is edge-on. Set `orient: "billboard"` on the system and every card turns to the camera at the frame's `motionTime` (it follows an animated camera, in render jobs and `scene_look`, and costs no extra vertices); `spin` rolls the card in its own plane. Without it, set `doubleSided: true` and `orient: "random"`, or use a `box` or low-poly sphere.
3. `scale: "grow"` starts every particle at size 0 and reaches full size at death; `"shrink"` does the reverse. A short life with `grow` is mostly tiny.
4. `alpha` and `color` become vertex colours and `alpha` multiplies the colour, so a particle fades toward black. On an `alphaMode: "add"` material black adds nothing, so the fade works; on an opaque or `blend` one the particle turns black against the background. For a see-through fade on a `blend` material add `fade: "opacity"` to the system (with `alpha`, such as `[0.6, 0]`): the colour keeps its brightness and the alpha becomes per-vertex opacity. It is refused on a node whose material is not `blend`, and the path tracer ignores it.
5. `floor`. It stops a particle that is born above that height and reaches it; the particle then stays where it landed until it dies (with `bounce` above 0 it bounces instead). A particle born below `floor` ignores it. Combined with `scale: "shrink"` or an `alpha` fade, particles that landed vanish where they lie.
6. Size. `size` is the scale of the node's geometry in metres: a unit `plane` with `size` 0.002 is 2 mm.

## Spray, dust and sparks

Spray is many small cards, born in a short window, flung up and pulled back by gravity and `drag`:

```json
{ "expectedRevision": 1, "operations": [
  { "type": "add-geometry", "geometry": { "id": "card", "type": "plane", "segments": 1 } },
  { "type": "add-material", "material": { "id": "mist", "tag": "unlit", "color": [0.9, 0.95, 1], "alphaMode": "add", "opacity": 0.5, "doubleSided": true } },
  { "type": "add-node", "node": { "id": "spray", "geometry": "card", "material": "mist" } },
  { "type": "set-particles", "particles": { "systems": [
    { "node": "spray", "seed": 11, "count": 700, "rate": 1800, "start": 0.5, "stop": 1.5, "lifetime": [0.5, 1.1],
      "speed": [2, 5], "spread": 40, "size": [0.04, 0.11], "drag": 0.8, "orient": "random", "scale": "shrink",
      "emitter": { "shape": "sphere", "position": [0, 0.4, 0], "radius": 0.3 } }
  ] } }
] }
```

Dust drifts: low speed, long life, high drag, and a gentle lift through the section `gravity` (default `[0, -9.81, 0]`). The section's `wind` moves
emitter particles only where `drag` is above 0.

```json
{ "expectedRevision": 1, "operations": [
  { "type": "add-geometry", "geometry": { "id": "speck", "type": "box", "bevel": 0 } },
  { "type": "add-material", "material": { "id": "dust", "tag": "unlit", "color": [0.7, 0.62, 0.5], "alphaMode": "add", "opacity": 0.35 } },
  { "type": "add-node", "node": { "id": "dust", "geometry": "speck", "material": "dust" } },
  { "type": "set-particles", "particles": { "gravity": [0, 0.05, 0], "wind": [0.4, 0, 0], "systems": [
    { "node": "dust", "seed": 5, "count": 400, "rate": 80, "lifetime": [2, 4], "speed": [0.1, 0.6], "spread": 180, "size": [0.02, 0.06],
      "drag": 1.5, "alpha": [1, 0], "emitter": { "shape": "box", "position": [0, 0.5, 0], "halfExtents": [1.5, 0.4, 1.5] } }
  ] } }
] }
```

Sparks are a third kind: `type: "sparks"` with `preset: "explosion"` throws bright cooling streaks. Its node needs a material with `tag: "unlit"` and `color: [1, 1, 1]`;
any other tag is refused with a message that says so. `floor` stops them on the ground, `bounce` (0 to 1) bounces them, `temperature` is `[start, end]` kelvin with start at or above end.

```json
{ "expectedRevision": 1, "operations": [
  { "type": "add-geometry", "geometry": { "id": "spark", "type": "box", "bevel": 0 } },
  { "type": "add-material", "material": { "id": "spark", "tag": "unlit", "color": [1, 1, 1] } },
  { "type": "add-node", "node": { "id": "sparks", "geometry": "spark", "material": "spark" } },
  { "type": "set-particles", "particles": { "systems": [
    { "type": "sparks", "preset": "explosion", "node": "sparks", "position": [0, 0.5, 0], "seed": 1758, "count": 400, "floor": 0 }
  ] } }
] }
```

Other fields: `instances` (up to 8 nodes, one drawn per particle), `color` `[[r, g, b] birth, [r, g, b] death]`, `colliders` (up to 8 static nodes), `bounce`, `friction`, `spin`, force `fields`.
A system with `colliders`, `bounce` or force fields is stepped at 1/120 s, so a seek back costs the particle's age in steps.

## Check a system

`scene_inspect` returns the `particles` report: per system the particle count, `verticesPerParticle`, `maxAlive` (the most alive at once) and `endsAt` (when the last one dies). Read it before the picture:
a `maxAlive` of 3 for a spray means `rate` is too low or the window too short. Seeking is exact: the same `motionTime` gives the same particles, in any order, and raising `count` keeps the earlier ones.
Sample a burst with `scene_review` shots at different `motionTime` values (for example just after `start`, at the middle, near `endsAt`).

## Sea spray, foam and wake

An `ocean` mesh edit writes a `foam` vertex group, as much as the wind's real whitecaps cover; a small patch may have none, so raise `coverage` (up to 1, six times the whitecaps) and keep foam with `foamMemory` (seconds). With `spray: true` it also writes a `spray` group (where the surface rises) and a `spray` velocity vector. A system takes droplets from the strong crests:

```json
{ "expectedRevision": 1, "operations": [
  { "type": "add-geometry", "geometry": { "id": "sea", "type": "mesh", "base": { "type": "box", "bevel": 0 },
    "edits": [ { "op": "subdivide", "levels": 4 }, { "op": "ocean", "windSpeed": 12, "choppiness": 2, "size": 2, "resolution": 4, "time": 1.5, "seed": 3, "coverage": 1, "foamMemory": 2, "spray": true } ] } },
  { "type": "add-geometry", "geometry": { "id": "speck", "type": "box", "bevel": 0 } },
  { "type": "add-material", "material": { "id": "water", "color": [0.1, 0.3, 0.5] } },
  { "type": "add-material", "material": { "id": "foam", "color": [0.9, 0.95, 1] } },
  { "type": "add-node", "node": { "id": "surface", "geometry": "sea", "material": "water" } },
  { "type": "add-node", "node": { "id": "droplet", "geometry": "speck", "material": "foam" } },
  { "type": "set-particles", "particles": { "systems": [
    { "node": "droplet", "count": 400, "speed": [0, 1], "lifetime": [0.6, 1.4], "size": 0.05, "scale": "shrink",
      "emitter": { "shape": "mesh", "mesh": "surface", "from": "vertices", "group": "spray", "groupThreshold": 0.3, "velocityFrom": "spray", "velocityScale": 2 } }
  ] } }
] }
```

- `mesh` names the node, not the geometry. The droplets read the mesh after its `edits`; a sea that carries floating bodies keeps its `ocean` op in the geometry `stack` instead (`physics.ocean.geometry`).
- Spray exists only where the foam folds: `choppiness` 0 sprays nowhere. A sea with no spray at its `time` refuses the scene with "no weight in vertex group spray": raise `windSpeed` or `choppiness`, lower `groupThreshold`, or change `time`.
- A sea moved by an `oceanTime` geometry track is followed: each droplet leaves the crests of the sea at its birth time.
- The edit's `wake: { points: [[x, z, strength, width]], height }` draws a trail you place; `physics` `float.boat.wake` fills it from a moving hull. Floating props ride the wave height; ocean `windSpeed` pushes nothing.

## Fog and beams

`environment.volumeFog` is one box: `density` 0 to 10, `steps` 8 to 48, `minimum` and `maximum` within 100000, `anisotropy` -0.9 to 0.9, `noiseAmount` 0 to 1, `drift` in units per second.
Point and spot lights scatter in it (at most 8, points first, no shadows, no light linking), and so does the sun. Up to 8 `localVolumes` (box, sphere, mesh part, grid) add smoke puffs or a glow in one place with no fog box.

```json
{ "expectedRevision": 1, "operations": [
  { "type": "set-environment", "environment": {
    "spotLights": [ { "position": [0, 4, 0], "direction": [0, -1, 0], "angle": 0.35, "penumbra": 0.6, "intensity": 400, "color": [1, 0.9, 0.7] } ],
    "volumeFog": { "density": 0.05, "minimum": [-6, 0, -6], "maximum": [6, 5, 6], "anisotropy": 0.5, "noiseAmount": 0.3 }
  } }
] }
```

- Open bug #2205: `scene_look` can fail with "WebGL render failed with error 1282" for a volume fog that combines `noiseAmount`, `drift`, `heightFalloff` and `color` on a physical sky, and the culprit field is not isolated. Add the fog fields one at a time with `scene_look` between, and keep the last set that renders. The fog block above (a spot light, `density`, `noiseAmount`, no `heightFalloff`, `drift` or `color`, default sky) rendered on a GPU backend without that error.
- A visible beam is a cone part, not a fog effect: give it an `alphaMode: "add"` material with a low `opacity`, stack two or three shells of growing radius, and fade each along its length with a `snippet` (see `materials.md`, "Shader hooks"). One shell shows a hard silhouette from the side.

## Not built yet

- Smoke and fire simulation inside the MCP tools. `add-explosion` bakes a blast (flash, fire and smoke grid, sparks, dust, rubble; see `effects-and-feedback.md`). For a puff, use emitter particles with `scale: "grow"` or a noisy `localVolumes` sphere with `emission`.
- Particles that follow a moving node: the emitter stays where `emitter.position` puts it in world space. Collision between particles, collision with a moving node and hair collision are not built either.
