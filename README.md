# Dockerfile Data Validation Pipeline

A production-grade, containerized data validation architecture demonstrating multi-stage Docker build integrity checks, schema contract enforcement, and OCI lineage metadata tracking.

---

## 🎯 Architecture Overview

This project provides an automated build-time barrier to prevent invalid or corrupted datasets from entering production pipelines:

```
Source Dataset + Schemas
         │
         ▼
┌──────────────────────────────────────────────┐
│ Stage 1: Validator Container                 │
│  - Executes PyTest suite                     │
│  - Verifies Pandera / Pydantic schema        │
│  - Asserts checksums & missingness bounds    │
│  - [Fails Docker build if validation errors] │
└──────────────────────┬───────────────────────┘
                       │ (Pass)
                       ▼
┌──────────────────────────────────────────────┐
│ Stage 2: Production Container                │
│  - Strips test tools & build artifacts       │
│  - Embeds OCI lineage metadata (ARG/LABEL)   │
│  - Runs as non-root user (appuser)           │
│  - Ready for deployment                      │
└──────────────────────────────────────────────┘
```

---

## 🚀 Key Features

1. **Multi-Stage Build Isolation:** Build-only test suites, pytest caches, and validation dependencies are isolated in the `validator` stage and excluded from the production image.
2. **Fail-Fast Build Boundary:** Docker build terminates with a non-zero exit code if schema mismatches, null thresholds, or invalid ranges occur.
3. **Data Governance & OCI Lineage:** Build arguments (`DATASET_VERSION`, `GIT_SHA`, `DATA_SOURCE_URI`) are attached as standard OCI labels, queryable with `docker inspect`.
4. **Security Best Practices:** Non-root execution (`USER appuser`), lean base images (`python:3.11-slim`), and minimal surface area.

---

## 📦 Quick Start

### Build with Validation:
```bash
docker build -t data-validator:1.2.0 .
```

### Inspect Lineage Metadata:
```bash
docker inspect --format='{{json .Config.Labels}}' data-validator:1.2.0 | jq
```

### Run Local PyTest Suite:
```bash
pip install -r requirements.txt
pytest tests/ -v
```

---

## 🛠️ Validation Tools Used
- **Pandera & Pydantic:** Schema contract definition and validation
- **PyTest:** Automated test runner for Docker build phase
- **PyArrow & Pandas:** High-performance data ingestion and checksum verification
