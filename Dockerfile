# Multi-Stage Dockerfile for Automated Data Validation & Production Packaging

# ----------------------------------------------------
# Stage 1: Validation & Integrity Check Environment
# ----------------------------------------------------
FROM python:3.11-slim AS validator

WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends     curl     && rm -rf /var/lib/apt/lists/*

# Install python validation dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source validation scripts, schemas, and dataset
COPY src/ /workspace/src/
COPY tests/ /workspace/tests/
COPY data/ /workspace/data/

# Run automated validation test suite.
# If any validation constraint, schema drift, or checksum fails, build halts immediately.
RUN pytest tests/test_data_integrity.py -v --disable-warnings

# Execute standalone schema & null assertion check
RUN python src/validate.py --dataset /workspace/data/sample_dataset.csv

# ----------------------------------------------------
# Stage 2: Final Minimal Production Runtime
# ----------------------------------------------------
FROM python:3.11-slim AS production

# Dynamic build arguments for lineage tracking
ARG DATASET_VERSION=1.2.0
ARG GIT_SHA=main
ARG DATA_SOURCE_URI=s3://data-lake/training/v1.2.0/

# OCI standard labels for lineage & auditability
LABEL org.opencontainers.image.title="Validated Data Container" \
      org.opencontainers.image.description="Container with verified data schemas and lineage metadata" \
      org.opencontainers.image.version="${DATASET_VERSION}" \
      org.opencontainers.image.revision="${GIT_SHA}" \
      dataset.lineage.source="${DATA_SOURCE_URI}" \
      dataset.validation.status="verified" \
      dataset.validation.engine="pandera-pytest"

WORKDIR /app

# Copy validated data from validator stage
COPY --from=validator /workspace/data /app/data
COPY --from=validator /workspace/src /app/src

# Run as non-root user for security governance
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

ENTRYPOINT ["python", "src/validate.py", "--dataset", "/app/data/sample_dataset.csv"]
