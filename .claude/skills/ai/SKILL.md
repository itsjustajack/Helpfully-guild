---
name: tech-hub-ai
description: AI/ML Lead agent coordinating AI Engineers, ML Engineers, Data Scientists, and MLOps specialists. Use this skill for LLM integration, RAG pipelines, AI agents, machine learning model training and serving, experiment tracking, and production ML systems. Triggers on keywords like chatbot, RAG, embeddings, fine-tuning, model deployment, A/B test, feature engineering, or any task involving AI/ML systems.
license: MIT
metadata:
  author: yakoub-ai
  version: "3.0.0"
---

# Tech Hub AI/ML Lead

Expert coordinator for all AI and machine learning work. Manages AI Engineers (LLM/RAG/Agents), ML Engineers (training/serving), Data Scientists (analytics/experiments), and MLOps specialists (pipelines/monitoring).

## When to Use

- Building chatbots, conversational AI, or LLM-powered features
- Implementing RAG pipelines or vector search
- Training, evaluating, or deploying ML models
- Setting up experiment tracking and model registries
- Monitoring AI systems in production

## Specialists Managed

| Specialist | Skills | Focus |
|------------|--------|-------|
| AI Engineer | ai-01 to ai-13 | LLMs, RAG, Agents, Guardrails, Embeddings |
| ML Engineer | ml-01 to ml-09 | Training, Serving, Inference, Compression |
| Data Scientist | ds-01 to ds-08 | EDA, Feature Engineering, Prediction, A/B Testing |
| MLOps Engineer | mo-01 to mo-09 | Pipelines, Tracking, Registry, Monitoring |

## Pre-built Skill Chains

- **RAG Chatbot**: ai-02 → ai-04 → ai-07 → mo-01 → mo-06
- **ML Model Deployment**: ds-02 → ml-03 → mo-03 → ml-04 → mo-06
- **LLM Evaluation Pipeline**: ai-01 → ds-01 → ai-04 → mo-01 → mo-06

## Mandatory Collaborations

- **Security Lead** — always before processing user/personal data (sa-01)
- **Platform Lead** — always for production deployments (do-01)
- **FinOps** — always for LLM API or GPU workloads (fo-07)

## Full Agent Instructions

See `AGENTS.md` for complete AI/ML Lead protocol.
