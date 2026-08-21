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

notebook:
    jupyter notebook notebooks/train.ipynb
