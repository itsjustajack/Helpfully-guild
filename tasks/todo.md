# To-do — Pixel Hero Card

> **CHANGE (Bailey, 2026-11-28): the characters must look EXACTLY as in his sheet. Do not redraw or change them.**
> The 16 characters (8 bodies, bare and in costume) are cut out pixel-exact in `games/style-guide/characters/`
> (0 differing pixels). My own hand-drawn hero card (T2 onward) is **parked**; the files stay in `games/pixel-hero/card/`.
> Next for characters: use these as the base-body and costume layers (no edits without Bailey's yes).

See `tasks/plan.md` for acceptance criteria and verification. Obsidian: "MHA RPG - To-do" mirrors this.

## Phase 1 — Hero card
- [x] T0 Checker first: `check_card.py` written and RED (done)
- [x] T1 Reference breakdown: measurements + `palette.json` + swatch (done: reference is ~255 art px tall, ~6 heads)
- [ ] ★ Checkpoint A: Bailey OK on palette, proportions AND the grid size (128x192 is too small for this reference)
- [ ] T2 Flat silhouette 128x192, landmarks ±3 px
- [ ] T3 Shaded body
- [ ] ★ Checkpoint B: Bailey "does the body read right?"
- [ ] T4 Head, face, shorts. Hair fully filled, no bald patch (checker test added)
- [ ] T5 Outline and polish, full Checker GREEN
- [ ] ★ CHECKPOINT C: Bailey judges the hero card (yes -> phase 2)

## Phase 2 — Layers (only after C = yes)
- [ ] T6 Split into body / hair / shorts / outline layers, recombine = 0 differing pixels
- [ ] T7 One shirt layer
- [ ] T8 One hair variant
- [ ] ★ Checkpoint D: Bailey decides what comes next

## Parked (not now)
Walking frames, enemies, maps, the city, engine choice.

## Approved
- [x] Isometric HD-2D city block v1 approved by Bailey (2026-11-28). Process in Obsidian: "Approved Process - Isometric HD-2D City Block".
- [ ] Next: skyline, bloom fix, tree variety, more blocks; hero costume test on a separate body copy.
