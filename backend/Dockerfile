# ============================================================
# Backend Dockerfile — Multi-stage build
# Stage: base → deps → development / production
# ============================================================

# ── Base Stage ───────────────────────────────────────────────
FROM python:3.12-slim AS base

LABEL maintainer="rugpull-detection-research"
LABEL description="Early Rug Pull Detection — FastAPI Backend"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ── Dependency Stage ─────────────────────────────────────────
FROM base AS deps

COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# ── Development Stage ─────────────────────────────────────────
FROM deps AS development

# Copy source code (mounted as volume in docker-compose)
COPY . .

# Create directories for artifacts
RUN mkdir -p /app/trained_models /app/datasets /app/logs

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ── Production Stage ──────────────────────────────────────────
FROM deps AS production

# Copy source
COPY . .

RUN mkdir -p /app/trained_models /app/datasets /app/logs

# Create non-root user for security
RUN addgroup --system rugpull && \
    adduser --system --ingroup rugpull rugpull && \
    chown -R rugpull:rugpull /app

USER rugpull

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
