# Plan: Pixel Hero Card, then Layers

Spec: Obsidian note "Pixel Hero Plan" (direction C, chosen by Bailey) + `games/style-guide/STYLE_GUIDE.md`.
Supersedes the old 3D plan (those files were removed; restore point git `c24715c`).
Rules from Bailey that apply: nothing reaches him until the Checker passes; judge side by side with the
reference, big and clear; never call a poor match good; one step at a time; body first, clothes second;
free tools only; no AI image generators; original art only.

## Goal and success
One front-facing MHA-style pixel hero (about 128x192) that Bailey looks at next to
`ref_hero_on_street.png` and says "yes, that's it". Then it becomes the body layer.

## Method (the bet to test)
The hero is **hand-placed on a pixel grid**: a text file where each character is a palette colour, one row
per pixel row. A small script turns it into a PNG (hard pixels, no blur). This is different from my failed
32x32 sprite, which was built from shapes. I look at every render myself, side by side with the reference.

## Where files go
`games/pixel-hero/card/`: `palette.json`, `hero_body.txt` (the grid), `build_card.py` (grid -> PNG + 8x preview),
`check_card.py` (the Checker), `previews/`. Old `games/pixel-hero/make_hero.py` stays untouched (superseded).

## Dependency graph
```
T1 Reference breakdown ──► T2 Silhouette (flat) ──► T3 Shaded body ──► T4 Head, face, shorts ──► T5 Outline + polish
        │                                                                                              │
        └─► palette.json ──────────────────────────────► (used by T3, T4, T5)                         ▼
                                                                                         ★ CHECKPOINT C: Bailey judges
                                                                                                      │ yes
                                                                                                      ▼
                                                                         T6 Split layers ──► T7 One shirt layer ──► T8 One hair variant
```
T1 blocks everything. T2 to T5 are strictly in order (each builds on the last picture). T6 to T8 only start
after Bailey says yes at Checkpoint C.

## Vertical slicing
Every task ends with a picture Bailey can look at (not a hidden layer or a half-built system).
Checker first (TDD): `check_card.py` is written before the art and fails until the art exists.

## Tasks

### T0 — Checker first (RED)
- Write `check_card.py`: file exists, size 128x192, transparent background, only hard pixels (alpha 0 or 255),
  palette ≤ 24 colours, no stray single pixels (orphan pixels) inside the figure, outline is continuous
  around the silhouette, left/right balance within tolerance.
- **Accept:** running it before any art fails with a clear message. **Verify:** run it, see RED.

### T1 — Reference breakdown
- Measure `ref_hero_on_street.png`: hero height in px, head size, shoulder/hip/knee/foot landmarks, pixel scale
  (screen px per art pixel). Extract a palette (≤ 24 colours) with 4-tone ramps for skin, hair, shorts, outline.
- **Accept:** a measurements table + `palette.json` + a swatch image. Proportions written in "heads".
- **Verify:** I overlay the landmarks on the reference and show Bailey the swatch.
- ★ **Checkpoint A:** Bailey OK on the palette and proportions.

### T2 — Flat silhouette (slice 1)
- Hand-place the whole figure in one flat tone per part (skin, hair, shorts) at 128x192, correct pose and proportions.
- **Accept:** Checker passes except shading/outline rules; landmarks within ±3 px of the scaled reference.
- **Verify:** side-by-side image: reference | my silhouette, enlarged 8x.

### T3 — Shaded body (slice 2)
- Add 3-4 tone ramps, light from the top-left, hue-shifted shadows; muscle forms (pecs, abs, arms, thighs), hands, feet.
- **Accept:** ≤ 24 colours, hard pixels, forms read (not a blob). **Verify:** side-by-side with the reference.
- ★ **Checkpoint B:** Bailey: "does the body read right?" (cheap place to change course).

### T4 — Head, face, shorts (slice 3)
- Hair with a lighter streak, simple readable face (eyes, brows, nose, mouth), ears, navy shorts, bare feet.
- **Accept:** face readable at 1x and at 8x; no orphan pixels. **Verify:** side-by-side + a 1x crop.

### T5 — Outline and polish (slice 4)
- Dark outline, selective inner lines, gold spawn ring under the feet, optional flat dusk background to compare.
- **Accept:** full Checker passes (all rules). **Verify:** Checker output + final side-by-side, big and clear.
- ★ **CHECKPOINT C (decision):** Bailey judges the hero card. Yes → T6. No → change the method (see risks).

### T6 — Split into layers (only after C = yes)
- Separate files: body, hair, shorts, outline; recombine to the same picture.
- **Accept:** recombined image is pixel-identical to the card. **Verify:** automatic diff = 0 differing pixels.

### T7 — One shirt layer
- A t-shirt as its own layer over the body. **Accept:** no body pixels poking through, no gaps at the hem/sleeves.

### T8 — One hair variant
- A second hairstyle layer swappable with the first. **Accept:** swap works, no leftover pixels of the old hair.
- ★ **Checkpoint D:** Bailey decides what comes next (walk frames, an outfit, the street).

## Risks and fallbacks
| Risk | Fallback |
|---|---|
| Hand-placed pixels can't reach the reference's detail | Lower detail (48x72), or Bailey touches it up in LibreSprite (free), or try 3D-to-pixel again as a last option |
| Proportions drift from the reference | Overlay check in T2; fix before shading |
| Bailey is overwhelmed by many pictures | One picture per checkpoint, big and clear, short message |

## Not in this plan
Walking frames, enemies, maps, the city, Blender or any 3D, AI image generators, the engine choice.
