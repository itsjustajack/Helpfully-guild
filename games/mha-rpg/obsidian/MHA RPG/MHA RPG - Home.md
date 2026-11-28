---
title: MHA RPG - Home
type: moc
tags: [moc, mha-rpg]
status: growing
created: 2026-11-27
updated: 2026-11-27
summary: "Entry point for the My Hero Academia open-world RPG fan project"
---

# MHA RPG — Home

Fan project, not for sale. **Idea (draft, needs Bailey's yes):** a Skyrim-style open-world action RPG in a superhero Japan — make your own hero, pick a Quirk that costs your body something real, and be a Hero student, a Villain or a Vigilante.

**Stage:** 2 — Pre-production. **Now: pixel hero card first** ([[Pixel Hero Plan]]). The 3D character files were removed.

## Plan
- [[MHA RPG - Production Plan]]
- [[MHA RPG - To-do]]
- [[MHA RPG - Production Brief]]
- [[MHA RPG - Decisions]]
- [[MHA RPG - Mistakes Log]]
- [[Pixel Hero Plan]]
- [[Style Guide]]

## Design (summaries of Bailey's PDFs)
- [[MHA RPG - Design Concept]]
- [[MHA RPG - Systems Spec]]

## Assets (the 3D ones are marked removed)
- [[Male Base Body]]
- [[Hand Base]]
- [[Mid-Gauntlet]]
- [[Hero Glove]]
- [[Underwear Layer]]
- [[Hero Rig]]
- [[Anime Look]]
- [[MHA Hero Tools Add-on]]
- [[Pixel Hero Test]]

## Asset dashboard
```dataview
TABLE asset_type AS "Type", tris AS "Tris", budget AS "Budget", qa AS "Checker", status AS "Status"
FROM #mha-rpg/asset
SORT file.name ASC
```

## Open decisions
```dataview
LIST summary
FROM #mha-rpg/decision
WHERE status = "open"
```

## Recently updated
```dataview
TABLE updated
FROM #mha-rpg OR #mha-rpg/asset OR #mha-rpg/decision OR #mha-rpg/design
SORT updated DESC
LIMIT 10
```
