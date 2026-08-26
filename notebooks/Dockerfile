FROM jupyter/base-notebook

# Switch to root to install system packages
USER root

# System dependencies you need for ML, cryptography, RL, etc.
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    cargo \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Switch back to notebook user
USER ${NB_UID}

# Workspace
WORKDIR /app

# Copy your project
COPY . /app

# Upgrade pip
RUN pip install --upgrade pip

# Install your project dependencies
RUN pip install -r requirements.txt

# Install MLflow + OpenTelemetry
RUN pip install mlflow \
    opentelemetry-api \
    opentelemetry-sdk \
    opentelemetry-exporter-otlp-proto-http

# Ensure notebooks directory exists
RUN mkdir -p /app/notebooks

ENV PYTHONPATH=/app

