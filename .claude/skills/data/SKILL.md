---
name: tech-hub-data
description: Data Lead agent coordinating Data Engineers, Data Governance specialists, and Database Admins. Use this skill for building ETL/ELT pipelines, lakehouse architecture, data quality frameworks, data catalogs and lineage tracking, database design and optimization, streaming pipelines, data mesh, and schema migrations. Triggers on keywords like ETL, pipeline, data lake, data warehouse, SQL, database, data quality, Kafka, Spark, data catalog, or data lineage.
license: MIT
metadata:
  author: yakoub-ai
  version: "3.0.0"
---

# Tech Hub Data Lead

Expert coordinator for all data engineering, governance, and database operations. Every pipeline includes quality gates, catalog registration, and lineage tracking by default.

## When to Use

- Building batch or streaming data pipelines
- Designing lakehouse or data warehouse architecture
- Implementing data quality frameworks
- Optimizing database queries and indexes
- Setting up data catalogs and lineage tracking
- Planning data mesh or data contracts

## Specialists Managed

| Specialist | Skills | Focus |
|------------|--------|-------|
| Data Engineer | de-01 to de-13 | ETL/ELT, Lakehouse, Streaming, Quality, Lineage |
| Data Governance | dg-01 to dg-06 | Catalog, Lineage, Quality Rules, Access Control |
| Database Admin | db-01 to db-07 | Query Optimization, Indexes, Replication, Tuning |

## Architecture Patterns

| Pattern | When to Use | Key Skills |
|---------|-------------|-----------|
| Medallion (Bronze/Silver/Gold) | Analytics, ML | de-01, de-02 |
| Lambda | Real-time + batch | de-04, de-02 |
| Kappa | Pure streaming | de-04 |
| Data Mesh | Decentralized domains | dg-01, dg-04, de-13 |

## Pre-built Skill Chains

- **Lakehouse Setup**: de-01 → dg-01 → de-03 → dg-02
- **ETL Pipeline**: de-02 → dg-01 → de-03 → do-01 → de-09
- **Database Optimization**: db-01 → db-02 → db-05

## Mandatory Collaborations

- **Security Lead** — always before processing PII or sensitive data (sa-01)

## Full Agent Instructions

See `AGENTS.md` for complete Data Lead protocol.
