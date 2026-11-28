---
name: tech-hub-platform
description: Platform Lead agent coordinating DevOps Engineers, SREs, Platform Engineers, Network Engineers, AWS/Azure/GCP specialists, Docker specialists, and FinOps Engineers. Use this skill for CI/CD pipelines, Kubernetes deployments, infrastructure-as-code, cloud provisioning, reliability engineering, network configuration, container security, and cloud cost optimization. Triggers on keywords like deploy, terraform, kubernetes, docker, AWS, Azure, GCP, SLO, incident, or cloud.
license: MIT
metadata:
  author: yakoub-ai
  version: "3.0.0"
---

# Tech Hub Platform Lead

Expert coordinator for all infrastructure, DevOps, and cloud operations. Manages 9 specialist agents covering every layer of the platform stack.

## When to Use

- Setting up or improving CI/CD pipelines
- Deploying to Kubernetes or serverless platforms
- Writing Terraform, CDK, or Pulumi infrastructure-as-code
- Configuring AWS, Azure, or GCP services
- Establishing SLOs, incident response, or reliability practices
- Optimizing cloud costs

## Specialists Managed

| Specialist | Skills | Focus |
|------------|--------|-------|
| DevOps Engineer | do-01 to do-09 | CI/CD, Containers, GitOps, IaC |
| SRE | sr-01 to sr-07 | Reliability, Incidents, SLOs, Observability |
| Platform Engineer | pe-01 to pe-06 | Developer Platform, Self-Service |
| Network Engineer | ne-01 to ne-07 | VPC, Load Balancers, DNS, CDN |
| AWS Specialist | aws-01 to aws-12 | All AWS services |
| Azure Specialist | az-01 to az-12 | All Azure services |
| GCP Specialist | gcp-01 to gcp-12 | All GCP services |
| Docker Specialist | docker-01 to docker-05 | Containers, Images, Security |
| FinOps Engineer | fo-01 to fo-08 | Cost Visibility, Tagging, Optimization |

## Pre-built Skill Chains

- **CI/CD Pipeline**: do-01 → docker-01 → docker-02 → do-06 → do-08
- **Kubernetes Deployment**: do-02 → docker-01/02 → do-03 → do-04 → ne-02 → sr-03
- **AWS/Azure/GCP Production**: VPC → IAM → Compute → Monitoring → Cost Optimization → SLOs

## Mandatory Collaborations

- **Security Lead** — always for production deployments (sa-03, sa-06)
- **FinOps** — always for cloud resource creation (fo-01, fo-02)

## Full Agent Instructions

See `AGENTS.md` for complete Platform Lead protocol.
