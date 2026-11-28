---
name: tech-hub-mcp
description: MCP Manager for Model Context Protocol server lifecycle, token optimization, and context-efficient external data access. Use this skill to activate MCP servers on-demand, optimize data fetches to minimize token consumption, audit server usage, manage server lifecycle, and catalog available MCP integrations. Triggers on keywords like MCP server, tool activation, token budget, context optimization, GitHub MCP, database MCP, or external data access.
license: MIT
metadata:
  author: yakoub-ai
  version: "3.0.0"
---

# Tech Hub MCP Manager

Expert in Model Context Protocol server lifecycle and token-efficient external data access. Core principle: **activate only what is needed, deactivate immediately**.

## When to Use

- Activating MCP servers for specific tasks (GitHub, Postgres, Slack, etc.)
- Optimizing token consumption when fetching external data
- Auditing which MCP servers are active and why
- Setting up MCP integrations for a new project
- Deactivating idle servers after tasks complete

## Skills

| Skill ID | Name | Purpose |
|----------|------|---------|
| mcp-01 | MCP Server Registry | Catalog available servers and their capabilities |
| mcp-02 | Dynamic Activation | Activate servers on-demand with audit logging |
| mcp-03 | Context Optimization | Minimize tokens per fetch with outline-first patterns |
| mcp-04 | Lifecycle Management | Track activations, detect idle servers, deactivate |
| mcp-05 | Server Catalog | Document query templates and cost profiles |

## Token Savings by Data Type

| Data Type | Strategy | Savings |
|-----------|----------|---------|
| Files | Outline first, then sections | 60–80% |
| Database | SELECT specific columns only | 70–90% |
| APIs | Paginate, filter, cache | 50–70% |
| Code | Symbol search, not full files | 80% |

## Full Agent Instructions

See `AGENTS.md` for complete MCP Manager protocol.
