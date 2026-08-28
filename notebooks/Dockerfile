FROM python:3.11-slim-bookworm AS base


ARG GPU=false

USER root

RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip

RUN pip install torch torchvision torchaudio


COPY notebooks/requirements.txt /tmp/requirements-jupyter.txt

RUN pip install --no-deps -r /tmp/requirements-jupyter.txt

RUN pip install -r /tmp/requirements-jupyter.txt

RUN mkdir -p /app/notebooks

ENV PYTHONPATH=/app

COPY docker/notebooks-entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8888

ENTRYPOINT ["/entrypoint.sh"]
