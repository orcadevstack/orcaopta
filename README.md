# orcaopta

Cloud ML project for anomaly detection, forecasting, resource optimization, and autoscaling.

## Structure

- `src/ml/` – ML training and inference modules
- `src/api/` – FastAPI service exposing ML endpoints
- `models/` – Saved model artifacts
- `docker/` – Dockerfile and container configs
- `terraform/` – Infrastructure-as-code for cloud deployment
- `ci-cd/github/` – GitHub Actions workflows
- `ci-cd/gitlab/` – GitLab CI/CD pipeline configs

## Run locally

```bash
pip install -r requirements.txt
uvicorn src.api.main:app --reload
