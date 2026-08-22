# Orcaopta Makefile

install:
    python -m venv .venv
    .venv/bin/pip install -r requirements.txt

test:
    pytest

train:
    python scripts/train_models.py

run-api:
    uvicorn src.api.main:app --host 0.0.0.0 --port 8000

docker-build:
    docker build -t orcaopta-api -f docker/Dockerfile .

docker-run:
    docker run -p 8000:8000 orcaopta-api

terraform-dev:
    cd terraform && terraform apply -var="cloud=aws" -var="environment=dev"

terraform-staging:
    cd terraform && terraform apply -var="cloud=azure" -var="environment=staging"

terraform-prod:
    cd terraform && terraform apply -var="cloud=gcp" -var="environment=prod"

-

notebook:
    jupyter notebook notebooks

notebook-ml:
    jupyter notebook notebooks/ml_train.ipynb

notebook-eval:
    jupyter notebook notebooks/evaluate.ipynb

notebook-explain:
    jupyter notebook notebooks/explain.ipynb

notebook-tune:
    jupyter notebook notebooks/tune.ipynb

notebook-mlflow:
    jupyter notebook notebooks/mlflow.ipynb

notebook-rl-train:
    jupyter notebook notebooks/rl_train.ipynb

notebook-rl-eval:
    jupyter notebook notebooks/rl_evaluate.ipynb

notebook-rl-mlflow:
    jupyter notebook notebooks/rl_mlflow.ipynb

notebook-rl-explain:
    jupyter notebook notebooks/rl_explain.ipynb

notebook-rl-compare:
    jupyter notebook notebooks/rl_compare.ipynb


notebook-all:
    jupyter notebook notebooks

compose-up:
    docker-compose up --build

compose-down:
    docker-compose down

compose-restart:
    docker-compose down && docker-compose up --build

compose-logs:
    docker-compose logs -f

compose-mlflow:
    docker-compose exec mlflow bash

compose-minio:
    docker-compose exec minio bash

compose-api:
    docker-compose exec api bash

compose-trainer:
    docker-compose exec rl-trainer bash