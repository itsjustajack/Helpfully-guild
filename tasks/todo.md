# Pocket task list

> **Correction, 11 Nov (read this first).** This plan was written before the Google Drive project
> document was read. That document says Pocket is already at **version 1.6 with 83 passing tests**, so
> most tasks below are **already built**: one doorway for taps, gates, tick-box cards, Stop all, Calm
> mode, OK and copy, share by file, the phone model download ("Get the AI") and the off-screen service.
> It also shows that **Online AI on the PC is Jack's own choice** (off by default, falls back to the PC
> model), so the "left out" table and Open Questions 2, 3 and 4 below are wrong.
>
> What still looks open, from that document: trying 1.6 on the real PC and phone (never confirmed),
> setting the context size for "Sort it", a wording mismatch on the Do gate, an out-of-date install
> guide, and locking the share file (it is plain text today). **Treat the rest of this file as a
> draft to be rewritten once the real code can be checked.**

Full details for each task are in `tasks/plan.md`. Status: **waiting for Jack's review.**

## Before anything
- [ ] Jack answers the 7 open questions in `tasks/plan.md`

## Phase 0: Find out what already exists
- [ ] Task 0: Compare today's Pocket with the report (XS)
- [ ] **Checkpoint 0:** plan updated with real file paths

## Phase 1: Pocket never loses or changes things by surprise
- [ ] Task 1: Saving cannot corrupt the file (S)
- [ ] Task 2: One doorway for every tap (M)
- [ ] Task 3: Do / Ask me / Never switches (S)
- [ ] **Checkpoint 1:** tests pass, forced-kill test loses nothing, Jack reviews

## Phase 2: A brain dump becomes cards on the PC
- [ ] Task 4: Ask the PC model for a fixed shape (S)
- [ ] Task 5: Check every answer before showing it (S)
- [ ] Task 6: Answers appear as unticked cards (M)
- [ ] Task 7: Stop all works straight away (S)
- [ ] Task 8: Tricky text stays as text (M)
- [ ] Task 9: Try it on Jack's real brain dumps (S)
- [ ] **Checkpoint 2:** PC path works end to end, Jack reviews results

## Phase 3: The same thing on the phone, offline
- [ ] Task 10: New phone model with a fixed answer shape (M)
- [ ] Task 11: Measure real phone speed (XS)
- [ ] Task 12: Switch to the smaller model (S)
- [ ] Task 13: Typing box stays above the keyboard (M)
- [ ] **Checkpoint 3:** works in airplane mode, real speeds written down, Jack reviews

## Phase 4: Calmer screen and safe copying
- [ ] Task 14: Calm mode shows three (S)
- [ ] Task 15: OK and copy (S)
- [ ] **Checkpoint 4:** Jack tries both on PC and phone

## Phase 5: Sharing between phone and PC
- [ ] Task 16: Export and import a share file (M)
- [ ] Task 17: Clashes become cards (S)
- [ ] Task 18: Lock the share file (S)
- [ ] Task 19: Pair by QR code (optional, last) (M)
- [ ] **Checkpoint 5:** full airplane-mode run, one share round trip, Jack signs off

## Can run side by side
- Tasks 13 and 14 (screen work) alongside Phase 2
- Task 16 alongside Phase 3, once Task 8 is done
