# Orcaopta MLflow MLOps Setup

This directory contains all MLflow-related configuration, metadata, and automation
for the Orcaopta MLOps pipeline.

## Structure

- artifacts/  
  MLflow artifacts (models, metrics, plots)

- registry/  
  Model registry metadata (staging, production, archived)

- configs/  
  MLflow server config, MLflow agent config, OpenTelemetry config

- scripts/  
  Automation scripts for model promotion, listing, downloading, and cleanup

- traces/  
  Optional OpenTelemetry trace storage

## Usage

### Train models
docker-compose run train

### Promote model to production
python mlflow/scripts/promote_model.py

### View MLflow UI
http://localhost:5000

### View Traces
MLflow → Tracing tab
