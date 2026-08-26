FROM python:3.10-slim AS base

# -----------------------------
# System dependencies
# -----------------------------
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    cargo \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------
# Install Python dependencies
# -----------------------------
# Upgrade pip
RUN pip install --upgrade pip

# Install cryptography properly
RUN pip install cryptography --no-binary cryptography

# -----------------------------
# Environment variables
# -----------------------------
ENV OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=http://localhost:5000/v1/traces
ENV OTEL_EXPORTER_OTLP_TRACES_HEADERS="x-mlflow-experiment-id=0"

# -----------------------------
# Workspace
# -----------------------------
WORKDIR /app

COPY . /app

# Install project dependencies
RUN pip install -r requirements.txt

ENV PYTHONPATH=/app

# -----------------------------
# Trainer Stage
# -----------------------------
FROM base AS trainer
CMD ["bash", "-c", "python scripts/${TRAIN_SCRIPT}.py"]

# -----------------------------
# API Stage
# -----------------------------
FROM base AS api
EXPOSE 8000
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
