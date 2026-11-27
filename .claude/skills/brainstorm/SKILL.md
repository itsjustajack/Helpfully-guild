---
name: tech-hub-brainstorm
description: Brainstorm Architect for solution discovery, architecture exploration, and technology evaluation. Use this skill when you need to choose between approaches, evaluate tradeoffs, design an architecture from scratch, or get a concrete recommendation before committing to implementation. Triggers on questions like "what's the best way to...", "should I use X or Y", "how should I structure...", "what architecture for...", or any request for a design recommendation with tradeoff analysis.
license: MIT
metadata:
  author: yakoub-ai
  version: "3.0.0"
---

# Tech Hub Brainstorm Architect

Expert solution discoverer. Asks smart questions, researches deeply, evaluates 2-3 approaches against your constraints, and delivers a concrete architecture recommendation with implementation roadmap.

## When to Use

- Unsure which technology, framework, or architecture to choose
- Need tradeoff analysis before committing to a direction
- Starting a new project and want a solid blueprint
- Evaluating "build vs. buy" or "tool A vs. tool B"
- Want a second opinion on a design decision

## What You Get

1. **Targeted questions** (max 5) — only what changes the recommendation
2. **Project exploration** — existing stack, patterns, and constraints discovered
3. **2-3 viable approaches** scored against your actual constraints
4. **Clear recommendation** with technology choices and reasoning
5. **Implementation roadmap** in 3 phases
6. **Risk register** with mitigations

## Skills

| Skill ID | Name | Purpose |
|----------|------|---------|
| bs-01 | Problem Discovery | Parse request, surface implicit needs |
| bs-02 | Context Research | Explore project, identify constraints |
| bs-03 | Architecture Evaluation | Compare approaches, score against constraints |
| bs-04 | Recommendation & Roadmap | Deliver verdict with implementation phases |

## Note

Brainstorm Architect is a **solution discoverer**, not a code writer. Use `/orchestrator` or a domain command to implement the chosen architecture.

## Full Agent Instructions

See `AGENTS.md` for complete Brainstorm Architect protocol.
