# Production Brief: Player Hero (male base + Mid-Gauntlet + hero glove)

**Type:** character (player hero, original — not a canon MHA character)
**Target:** game engine — **Unreal Engine 5 (decided by Bailey)**, FBX export
**Style:** anime / cel (`anime-style`): 3-step cel shading + ink outline, per the design PDF section 3.1
**Platform:** PC
**Poly budget (whole character, LOD0):** 60,000 tris
| Part | Budget | Now |
|---|---|---|
| Base body `SM_MaleBase` | 20,000 | 16,048 ✅ |
| Hands (x2, part of body later) | 2 × 6,000 | standalone test hand 12,064 ⚠️ (merge into body, retopo) |
| Hero glove (x2) | 2 × 8,000 | 28,620 ❌ over — retopo needed |
| Mid-Gauntlet (x2) | 2 × 6,000 | 9,500 ⚠️ |
| Costume (later) | 12,000 | — |
**Texture budget:** 2048² for body, 1024² per gear piece (cel look needs little texture detail)
**Export:** UE5 → FBX (scale 1.0, +X forward fix, smoothing: face) · Godot → GLB (+Y up, Draco off for editing)
**Pivot:** world origin at the feet (body); gear parented to bones after rigging
**Animation:** rigged (Rigify humanoid), game skeleton for the chosen engine

## Rules from Bailey (`bailey-expectation`)
- Base body first, locked, bald; clothes and gear are separate objects on top.
- Nothing blocky reaches Bailey. Checker (`blender-asset-qa`) passes before anything is shown.
- Judge against Bailey's reference photo side by side, big and clear. Never call a poor match good.

## Active skills (pipeline order)
1. `character-artist` — body proportions, clothing as separate meshes
2. `blender-sculpting` — procedural sculpt pass (headless-safe); detailed brushwork by Bailey if wanted
3. `blender-hardsurface-modeling` — gauntlet and armor plates
4. `blender-retopology-uv` — game-ready topology + real UVs (replaces placeholder cylindrical UVs)
5. `blender-stylized-npr` / `anime-style` — cel shader + outline (`toon_look.py`)
6. `blender-character-rigging` — Rigify, skinning, gear parented to bones
7. `blender-export-pipelines` — UE5 or Godot preset
8. `blender-asset-qa` — gate after every step (automated test: `tests/test_male_base.py`)

## Pipeline phases
- [x] Reference & planning (Bailey's mannequin photo, design PDFs)
- [x] Blockout & silhouette (male base v1 → v8)
- [x] Modeling: body v8, Mid-Gauntlet, hand v2, hero glove with armor plates
- [x] Look test: anime cel shader + ink outline
- [ ] Cleanup & topology: retopo glove (28.6k → 8k) and hand; merge hand into body
- [ ] UVs: proper unwrap for all parts
- [ ] Materials/textures: cel palette per part
- [ ] Optimization: LODs (LOD1 50%, LOD2 25%)
- [ ] Rig: Rigify + weights; gear to bones
- [ ] Export & validation (needs engine decision)

## Next step (one)
Retopologize the hero glove to its 8,000-tri budget and re-run the Checker. It is the only part clearly over budget.
