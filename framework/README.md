# Framework Overview
Orcaopta is built on a modular, cloud‑native framework stack designed for high‑performance SRE analytics, ML‑driven automation, and large‑scale observability. Each layer of the stack is purpose‑built to support distributed computation, real‑time telemetry, intelligent remediation, and seamless integration with modern cloud platforms.

# 1. Core API Framework
## The Orcaopta API is powered by a fast, asynchronous microservice stack:
- FastAPI — High‑performance async API framework for orchestrating SRE workflows

- Uvicorn — Production‑grade ASGI server

- Pydantic — Strict typed models for telemetry, incidents, RCA, and remediation

- Requests — Cloud API integration (OpenStack, K8s, Terraform, ML services)

- This layer provides a clean, stable control plane for all Orcaopta components.

# 2. Machine Learning & Reinforcement Learning Framework
## Orcaopta uses a lightweight but powerful ML stack optimized for cloud‑scale SRE analytics:

- pandas — ETL, feature extraction, and metric processing

- scikit‑learn — Clustering, anomaly detection, forecasting, and classification

- joblib — Model persistence and caching

- shap — Explainability for ML‑driven incident prediction

- stable‑baselines3 — Reinforcement learning for autoscaling, optimization, and self‑healing policies

- gymnasium — RL environment framework for simulating cluster behavior

- This ML layer enables predictive SRE, automated decision‑making, and explainable RCA.

# 3. Observability & Telemetry Framework
## Orcaopta integrates deeply with modern observability ecosystems:

- OpenTelemetry API & SDK — Distributed tracing and metrics

- OTLP HTTP Exporter — Native integration with Jaeger, Tempo, Honeycomb, MLflow, and any - OTLP‑compatible backend

- This ensures end‑to‑end visibility across logs, metrics, traces, anomalies, drift, and remediation actions.

# 4. Cloud Orchestration Framework
## Orcaopta interacts directly with cloud infrastructure to perform remediation and automation:

- openstacksdk — Compute, network, block storage, identity, and orchestration

- kubernetes‑python — Pod lifecycle, deployments, autoscaling, node health, and cluster operations

- python‑hcl2 — Terraform plan parsing for drift detection and infrastructure consistency checks

- This layer enables self‑healing, auto‑remediation, and cloud‑aware RCA.

# 5. Dashboard & Visualization Framework
## Orcaopta provides a full enterprise SRE dashboard:

- Streamlit — Interactive UI for SLOs, anomalies, incidents, RCA, remediation, and forecasting

- Plotly — High‑resolution charts for latency, error rates, anomaly timelines

- PyVis — Graph visualization for RCA propagation, dependency graphs, and remediation flows

- NetworkX — Graph analytics for root‑cause propagation and service dependency modeling

- This creates a Grafana‑like experience without needing a separate frontend stack.

# 6. Security & Compliance Framework
## Security is built into the platform:

- cryptography — Secure hashing, encryption, and signing

- ossaudit — Vulnerability scanning for Python dependencies

This ensures Orcaopta is safe for enterprise environments.

# 7. AI / LLM Automation Framework
# Orcaopta integrates AI‑driven automation:

- hoppr‑cop — LLM orchestration for cloud automation, remediation suggestions, and RCA = explanation

- This layer enables intelligent SRE assistants, automated triage, and AI‑guided remediation.

# Summary

## The Orcaopta framework stack is:

Cloud‑native

Distributed

ML‑driven

Observability‑first

Self‑healing capable

Enterprise‑ready

It combines modern API design, lightweight ML, deep cloud integration, and rich visualization to deliver a complete SRE automation platform.