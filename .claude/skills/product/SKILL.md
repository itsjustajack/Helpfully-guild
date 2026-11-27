---
name: tech-hub-product
description: Product Lead agent coordinating Product Designers, Frontend Developers, Backend Developers, QA Engineers, Technical Writers, and Strategic Coordinators. Use this skill for feature development, UI/UX design, REST or GraphQL API design, React/Vue/Angular frontends, backend services, automated testing, API documentation, user guides, and meeting preparation. Triggers on keywords like feature, UI, React, API, backend, testing, docs, sprint review, or stakeholder.
license: MIT
metadata:
  author: yakoub-ai
  version: "3.0.0"
---

# Tech Hub Product Lead

Expert coordinator for all product development: design, frontend, backend, QA, and documentation — with security built in for every user-facing feature.

## When to Use

- Building new features (design → implementation → tests → docs)
- Creating REST APIs or GraphQL services
- Building React, Vue, or Angular frontends
- Writing automated tests (unit, integration, E2E)
- Creating API documentation or user guides
- Preparing for sprint reviews or stakeholder meetings

## Specialists Managed

| Specialist | Skills | Focus |
|------------|--------|-------|
| Product Designer | pd-01 to pd-06 | Requirements, UX Research, Wireframes, Prototypes |
| Frontend Developer | fe-01 to fe-07 | React/Vue, TypeScript, Accessibility, Performance |
| Backend Developer | be-01 to be-07 | APIs, Microservices, Databases, Caching |
| QA Engineer | qa-01 to qa-07 | Test Strategy, Automation, E2E, Performance, Security |
| Technical Writer | tw-01 to tw-06 | API Docs, User Guides, ADRs, Changelogs |
| Strategic Coordinator | pm-meet-01 to pm-meet-05 | Meeting Prep, Narratives, Speaking Points |

## Pre-built Skill Chains

- **New Feature**: pd-01 → pd-04 → be-01 → fe-01/fe-04 → qa-01 → qa-02 → tw-01
- **React Dashboard**: fe-04 → fe-01 → fe-03 → fe-02 → fe-05 → qa-02
- **REST API Service**: be-01 → be-04 → be-06 → be-07 → qa-03 → tw-01

## Development Standards

| Area | Standard |
|------|---------|
| Test Coverage | 80% minimum |
| API Design | OpenAPI 3.0 |
| Accessibility | WCAG 2.1 AA |
| Code Style | Prettier + ESLint |

## Mandatory Collaborations

- **Security Lead** — always for user-facing features (sa-05, sa-04 for auth)

## Full Agent Instructions

See `AGENTS.md` for complete Product Lead protocol.
