FROM python:3.12-slim-bookworm AS base

RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    cargo \
    pkg-config \
    curl \
    ceph-common \
    openvswitch-switch \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
#RUN pip install cryptography 

RUN pip install "kitaru[cli,mcp,worker]"

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY . /app

ENV PYTHONPATH=/app

ENV OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=http://localhost:5000/v1/traces
ENV OTEL_EXPORTER_OTLP_TRACES_HEADERS="x-mlflow-experiment-id=0"

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# -----------------------------
# API + MCP in one image
# -----------------------------
FROM base AS api

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

ENTRYPOINT ["/entrypoint.sh"]
