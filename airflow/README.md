# Airflow Configuration

This directory contains Apache Airflow configuration and DAGs for the PaperLens project.

## Current Setup (Week 1)

### DAGs
- **health_dag.py**: Hello world + service connectivity check (API health, PostgreSQL connection)

## Directory Structure

```
airflow/
├── README.md                    # This file
├── Dockerfile                   # Python 3.12 slim + Airflow 2.10.3 with PostgreSQL backend
├── entrypoint.sh                # DB init, admin user creation, webserver + scheduler startup
├── requirements-airflow.txt     # Python dependencies for DAG tasks
└── dags/
    ├── health_dag.py            # Week 1 health check DAG
    └── paper_ingestion/         # Week 2 (not yet implemented)
```

## Container Details
- **Base image**: `python:3.12-slim`
- **Airflow**: 2.10.3 with PostgreSQL backend
- **User**: `airflow` (UID 50000) for cross-platform compatibility
- **System deps**: build-essential, curl, libpq-dev, poppler-utils, tesseract-ocr (for Week 2 PDF processing)

## Usage

### Web Interface
- **URL**: http://localhost:8080
- **Credentials**: admin / admin_user

### Running
Started via Docker Compose:
```bash
docker compose up -d
```

### Service Dependencies
- **PostgreSQL**: Airflow metadata DB + PaperLens data (shared instance)
