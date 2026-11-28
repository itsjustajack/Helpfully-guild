---
title: Approved Process - Isometric HD-2D City Block
type: process
tags: [mha-rpg, background, approved, isometric]
status: approved
created: 2026-11-28
updated: 2026-11-28
summary: The one process Bailey approved ("That's it"): code-drawn iso pixel city block + HD-2D look pass.
---
# Approved: isometric HD-2D city block (Bailey: "That's it that's it", 2026-11-28)
Only this process is approved. The earlier straight-on street (dusk and day) and the kit tree are NOT approved; they are experiments.

## What was approved
`games/background/iso/make_iso.py` v1 -> `iso_block_x3.png` (pixel) and `iso_block_hd2d.png` (HD-2D look). Commit: "Isometric city block v1".

## The process (repeat this)
1. **Grid:** 2:1 pixel isometric, tile 32x16 px, art canvas 384x336 (shown 3x, nearest-neighbour). Screen x = OX+(gx-gy)*16, y = OY+(gx+gy)*8-height.
2. **Ground by inverse mapping:** for every pixel work out world (gx,gy), then colour from world position: road, sidewalk tiles, joints, curbs, zebra crossings, yellow lines. Textures stay continuous and clean.
3. **Cast shadows** as darker ground behind each building (toward the camera side).
4. **Diorama slab edge** (14 px thick) on the two front edges, like the painted room reference.
5. **Buildings as iso boxes:** two wall faces drawn column by column (left face darker, right face lit, light edge at the corner), each with: shop ground floor (awning stripes, sign band, glass), floor ledges, windows with frames (lit yellow vs dark), brick rows with noise, cornice, textured roof.
6. **Props:** leaf-cluster trees (lumps, 5 green tones, speckles) and lamps with warm heads. Draw order sorted by position (gx+gy), buildings by footprint centre.
7. **HD-2D look pass** on the 3x upscale only (the pixel art stays sharp): bloom on bright pixels, tilt-shift blur at top and bottom, vignette, warm grade.
## Rules used (see [[Style Guide]])
Clean lines, sharp silhouette, flat shading, no dithering (hard sky bands), distinct pixel clusters. Palette limit lifted.

## Known weak spots to improve next (Pip's own list)
Plain sky bands behind it, bloom hazing the bottom, small plain shopfronts, trees all the same, empty left side.
## Next
Skyline behind, bloom fix, tree variety, more blocks; hero costume test on a separate copy of the body (sheet characters stay unchanged).
