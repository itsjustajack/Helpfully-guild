# Plan — My Hero Academia Open-World RPG

Fan project, not for sale. Source spec: Bailey's two design PDFs plus `games/mha-rpg/PLAN.md` (the 8 stages). Standards: the `bailey-expectation` skill (5-star bar, Checker gate, no blocky shapes shown to Bailey).

## How work moves

Bailey → Planner → Designer → Checker → Bailey. Nothing reaches Bailey until the Checker passes it. One step at a time; each step ends with a report and a proposed next step.

**Blockout rule:** greybox blocks are internal to the team (stage 3 only). Bailey sees only finished-quality work or plain written plans.

## Dependency graph

```
Idea (1) ──► Engine pick (2a) ──► Tech setup (2c) ──► Prototype (3) ──► Vertical slice (4) ──► Production (5) ──► Alpha (6) ──► Beta (7) ──► Gold (8)
        └──► Design doc (2b) ───┘        ▲
                                 Asset pipeline (2d) ──► slice art (4)
```

- The engine decides everything after stage 2: tools, file formats, which collected repos are usable.
- The asset pipeline (Blender → engine) must work before any art can reach Bailey.
- Stage 3 needs the core design rules (Quirk heat/strain, movement, camera) written down first.

## Vertical slicing

Each task delivers one complete working path, not one layer. Example: "player uses a Quirk and the heat meter rises and hurts them" covers input + ability + meter + HUD + feedback together, not "build all HUD first".

## Stages and tasks

### Stage 1 — Idea
- **1.1 Lock the one-sentence idea.**
  Accept: Bailey says yes to the sentence and to who plays it.
  Verify: his yes is recorded in `games/mha-rpg/PLAN.md`.

**Checkpoint A:** idea locked.

### Stage 2 — Pre-production
- **2.1 Pick the engine** (Unreal Engine 5 or Godot).
  Accept: Bailey's choice recorded; free-tools rule (rule 14) still met.
  Verify: engine installs and opens an empty project on Bailey's PC.
- **2.2 Core design doc** — one page per system, plain words: Quirk types and body cost, use-to-improve progression, three paths (Hero / Villain / Vigilante), law and collateral meter, gear slots.
  Accept: every system traced to a PDF section; nothing invented without a "draft — needs Bailey's yes" tag.
  Verify: Checker compares doc against both PDFs, section by section.
- **2.3 Team and order of work** — which role owns which system (Lead Developer, Art Director, QA Director, Narrative Director, Story Writer, Lore Writer, World Builder Director).
  Accept: every system has one owner; Checker step named on each.
- **2.4 Project setup** — repo folder `games/mha-rpg/`, engine project, version control, build that runs.
  Accept: empty project opens and runs on Bailey's PC.
  Verify: Lead Developer runs it firsthand; screenshot.
- **2.5 Asset pipeline test** — one real model (the Blender glove test) goes Blender → engine with full PBR maps.
  Accept: model shows in engine with all maps, correct scale, no errors.
  Verify: Checker side-by-side render, big and clear.
- **2.6 Rough timeline** — exact dates per stage, worked out after 2.1–2.5.

**Checkpoint B:** engine chosen, design written, pipeline proven. Bailey sees the plan in plain words.

### Stage 3 — Prototype (internal greybox)
- **3.1 Movement and camera path** — walk / sprint / dodge-roll, third-person spring-arm camera, V switches camera.
  Accept: feels responsive; camera never clips through walls.
- **3.2 Quirk path** — one Quirk (e.g. Combustion Sweat): use it → damage → heat meter rises → overheat hurts the player.
  Accept: the body-cost loop works end to end.
- **3.3 Fight path** — one enemy, melee + Quirk, hit-stop, dodge.
  Accept: no auto-combo; stun has diminishing returns (PDF 4.3).
- **3.4 Law path** — using a Quirk in view of a camera raises the collateral / law meter.
- **3.5 Fun test** — team plays it, writes what is fun and what is not.
  Accept: written verdict; anything not fun is fixed or cut.

**Checkpoint C:** core loop is fun. Bailey gets a written summary only — no greybox images.

### Stage 4 — Vertical slice (Bailey sees this)
- **4.1 Slice scope** — one Musutafu street at golden hour, the player's original hero, one Quirk, one fight, one rescue.
- **4.2 Base body** — anatomically correct, bald, underwear, locked (rule 7).
- **4.3 Hero costume** — the six gear slots, layered on the base body.
- **4.4 Street art** — real PBR models only; nothing blocky.
- **4.5 Lighting and look** — cel shading + thick ink lines + 3D onomatopoeia (PDF section 3).
- **4.6 HUD** — clean comic-panel HUD near the character (PDF 3.3).
  Accept for every 4.x: passes Checker against reference photos, side by side, 1024px+, every side.

**Checkpoint D:** Bailey judges the slice with his own eyes.

### Stages 5–8 (planned in detail after Checkpoint D)
- **5 Production** — all districts, all three paths, all systems, sound.
- **6 Alpha** — feature freeze.
- **7 Beta** — bug fixing and polish only.
- **8 Gold** — final build, then patches.

## Blockers right now
1. Bailey's yes on the one-sentence idea (1.1).
2. Engine choice (2.1).
3. No 3D models exist yet — art steps stop until real models are made.
