---
name: tech-hub-orchestrator
description: Master AI orchestrator for complex, multi-domain engineering tasks. Use this skill when a task spans multiple disciplines (AI + DevOps, security + data, frontend + backend + QA), requires coordinated specialist agents, or needs structured plan-then-execute workflow with session continuity across multiple conversations. Triggers on requests like "build and deploy a full-stack app", "set up a secure data pipeline", or any task requiring more than one domain of expertise.
license: MIT
metadata:
  author: yakoub-ai
  version: "3.0.0"
---

# Tech Hub Orchestrator

The master entry point for all multi-domain engineering tasks. Brainstorms, plans, coordinates specialist agents, and synthesizes results — with full session continuity across conversations.

## When to Use

- Tasks that span multiple domains (AI + DevOps, security + data, frontend + backend)
- Complex projects requiring structured plan → execute → verify workflow
- Multi-session projects where state must be preserved across conversations
- Any task where you'd want a senior staff engineer to coordinate the work

## Available Domains

| Domain | Lead Agent | Trigger Keywords |
|--------|-----------|-----------------|
| AI/ML | AI/ML Lead | chatbot, LLM, RAG, model, prediction, embeddings, agent |
| Platform | Platform Lead | deploy, kubernetes, CI/CD, infrastructure, cloud, docker |
| Security | Security Lead | PII, compliance, IAM, vulnerability, GDPR, security |
| Data | Data Lead | pipeline, ETL, warehouse, quality, catalog, database |
| Product | Product Lead | feature, UI, API, testing, documentation, frontend, backend |
| Brainstorm | Brainstorm Architect | architecture, solution, design, tradeoff, "best way to" |

## Workflow

```
Resume (check prior session state)
  → Understand (explore project + analyze request)
    → Plan (select agents, sequence work, present for approval)
      → Execute (spawn lead agents in parallel batches)
        → Verify (run tests, check quality gates)
          → Synthesize (report results + save state)
```

## Full Agent Instructions

See `AGENTS.md` for complete orchestrator protocol.
