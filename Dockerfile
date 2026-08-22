FROM python:3.10-slim AS base

# System dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create workspace
WORKDIR /app

# Copy project
COPY . /app

# Upgrade pip
RUN pip install --upgrade pip

# Install dependencies system-wide
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
