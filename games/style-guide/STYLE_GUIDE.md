# Pixel Style Guide (from Bailey's two reference pictures)

Bailey's rule: reference photos set the FEEL. They are references to learn from, never to copy.
Everything we make is original and drawn/built by us (no AI image generators, no copied art).

References (saved in `references/`):
- `ref_hero_on_street.png` — a muscular pixel hero standing on a pixel city street at dusk.
- `ref_city_street.webp` — a daytime pixel city street in strong one-point perspective.
- `ref_painted_iso_room.jpg` — a painted, moody isometric cutaway room with two characters (the "records office" picture).
- `ref_character_creator_sheet.png` — a sheet of 8 pixel body types, bare (top row) and in costume with hair (bottom row).

## What the pictures show

**Character (ref_hero_on_street)**
- Detailed "modern" pixel art, not chunky 8-bit: real anatomy (V-taper torso, abs, defined legs and hands).
- Standing front view, relaxed, weight on one leg. Short dark hair with one lighter streak. Navy shorts, barefoot.
- Shading is hard colour bands (3-5 tones per colour), warm highlights, cooler shadows.
- A dark outline around the character; lighter, selective lines inside.
- A gold ring under the feet (spawn/selection marker).

**Backgrounds (both pictures)**
- Strong one-point perspective: a street running to a vanishing point, tall buildings on both sides.
- Buildings built from window grids, ledges and signs; trees as round clusters shaded in flat tone stripes.
- Dithering (checker patterns) for sky gradients and soft shadows.
- Dusk version: blue-purple, dark vignette at the edges, warm skin as the accent.
- Day version: saturated orange / red / blue buildings, cyan sky, white pixel clouds, yellow centre line.

## Third reference: the painted isometric room (ref_painted_iso_room)
This one is a painted illustration, not pixel art. It sets the mood for interiors and for any "painted" scenes.
- **Cutaway diorama:** high isometric view, two back walls kept, the front walls cut low (brick wall in front).
- **Dark and moody:** the room is dark; warm pools of light from a desk lamp and a wall lantern; cool light from a window.
- **Dense props:** shelves full of archive boxes, papers on the desk, books, a plant, a notice board, framed pictures, a rug.
- **Same style for people and room:** the characters are painted exactly like the room (same brushwork, same lighting), never a different style pasted in.
- **Characters seen from above and behind:** a man in a dark coat with a satchel, a woman with auburn hair in a vest, both facing the desk; hair and shoulders read clearly.
- **Materials look painted:** worn wood, brick, plaster, paper. Warm browns and ambers against deep shadow, one teal/green accent (the lamp, the book, the vest).
- **UI frame:** parchment banner at the top, round cream icon buttons on the left edge (Recent, Archive, Settings) with small icons and labels.

## Fourth reference: the character-creator sheet (ref_character_creator_sheet)
This shows the **system** we are building toward, in the same pixel style as the hero-on-the-street picture.
- **8 body presets:** male and female, each skinny / slim / athletic / heavy. Same front view, same pose, same street, same gold ring.
- **Two rows:** top = bare base body (bald, plain underwear/shorts/sports top); bottom = the same bodies in a costume with hair.
- **The base body is its own layer.** Hair and costume are layers on top. The face and head look the same across bodies.
- **The costume is fitted per body.** It follows each body's shape (broad, narrow, curvy, heavy), it is not one overlay stretched over all of them.
- **Costume example:** red vest and trousers, blue sleeves and collar, yellow gloves and tall boots, black belt with a buckle and pouches, black swept hair with a lighter streak.
- **Visible risk in the sheet:** on the heavy bodies the costume has stray lines and small tears at the hips and hands, where the costume layer does not match the body. That is the alignment problem to avoid.
- **Our hero card is the "Male athletic" preset** (first target); the other presets come only after it works.

## Which look is used where (Bailey decides)
The pixel pictures and the painted room are two different looks. Until Bailey says otherwise: pixel street and pixel hero = the pixel game; painted room = interiors and mood. The one rule above all: **inside one picture, everything shares one style.**

## Rules we follow (every artist and every tool)
1. **One pixel grid.** Character and background share the same pixel size. Never mix resolutions.
2. **Hard pixels only.** Nearest-neighbour scaling. No blur, no anti-aliasing, no smooth gradients.
3. **Limited palette with colour ramps.** 3-5 tones per hue. One shared palette per scene.
4. **Hue-shifted shading.** Shadows lean cool (blue/purple), highlights lean warm.
5. **Dither for gradients** (sky, fog, soft shadows). Never a smooth fade.
6. **Dark outline on characters**, so they stand out from the background.
7. **Body first, clothes second.** Anatomically correct base body; clothes are separate layers on top (Bailey's body rule).
8. **Character readable at game size**: strong silhouette, face and hands clear.
9. **Perspective stays consistent** within a scene (one vanishing point).
10. **Judge side by side** with the references, big and clear. Say plainly when it does not match.

## Estimates (not measured)
- The art looks about 3-4 screen pixels per art pixel; the hero is about 60% of the picture height.
  Treat these as starting guesses, to be tuned when we compare.


## HD-2D rules (Bailey, 2026-11-28)
Source: his HD-2D note ("tattoos" in it was a voice-to-text slip for "photos", meaning the reference screenshots; no tattoos).
1. **Clean line work.** Crisp, continuous edges; no fuzzy or broken lines.
2. **Sharp silhouette.** The outline shape reads first, even as a flat black shape.
3. **Flat shading, minimal dithering.** Hard tone steps, no dotted gradients (sky bands are hard bands now).
4. **Distinct pixel clusters.** Group pixels into readable clumps (leaves, bricks, windows), not noise.
Test rule: try a new detail on minimal clothing / a plain body first, then add complex gear.
Palette is no longer strictly limited (Bailey: break that rule if something else helps).
