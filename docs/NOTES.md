
# Engineering Log & Technical Reference

This document serves as the technical diary and reference manual for the **Credit Card Transaction Pipeline**. It captures architectural decisions, configuration details, and lessons learned during development.

---

## 📚 Table of Contents
1. [Cloud Infrastructure (GCP)](#1-cloud-infrastructure-gcp)
2. [Data Transformation (dbt)](#2-data-transformation-dbt)
3. [Orchestration (Dagster)](#3-orchestration-dagster)
4. [Containerization (Docker)](#4-containerization-docker)
5. [CI/CD Pipeline](#5-cicd-pipeline)
6. [Security & Compliance](#6-security--compliance)

---

## 1. Cloud Infrastructure (GCP)

### The "Office Building" Analogy
* **GCP Project** (`total-compiler-477816-r3`) = The Office Floor.
* **BigQuery** = The Warehouse.
* **Datasets** = The Rooms:
    * `fraud_detection_raw`: Loading Dock (Raw Data).
    * `fraud_detection_dev`: Workshop (Testing).
    * `fraud_detection_prod`: Showroom (Production).
* **Service Account** (`dbt-fraud-detection`) = The Robot Employee.
    * **Badge:** `fraud-detection-key.json`.
    * **Access:** Limited strictly to the Warehouse.

### Setup Commands (Reference)
```bash
# 1. Authentication
gcloud auth login
gcloud config set project total-compiler-477816-r3

# 2. Dataset Creation (Singapore Region)
bq mk --location=asia-southeast1 --dataset fraud_detection_raw
bq mk --location=asia-southeast1 --dataset fraud_detection_dev
bq mk --location=asia-southeast1 --dataset fraud_detection_prod

# 3. IAM & Security
gcloud iam service-accounts create dbt-fraud-detection
# Grant Editor (Create Tables) and Job User (Run Queries)
gcloud projects add-iam-policy-binding total-compiler-477816-r3 --role="roles/bigquery.dataEditor" --member="serviceAccount:..."
gcloud projects add-iam-policy-binding total-compiler-477816-r3 --role="roles/bigquery.jobUser" --member="serviceAccount:..."
````

-----

## 2\. Data Transformation (dbt)

### Layered Architecture

  * **Staging (`stg_`)**: 1:1 mapping of source data. Type casting, renaming, basic cleaning. **(Materialized as Views)**.
  * **Intermediate (`int_`)**: Complex logic, joins, feature engineering (Z-scores, time features). **(Materialized as Views)**.
  * **Marts (`fct_`)**: Final business logic, aggregated metrics. **(Materialized as Tables)**.

### Optimization Strategy

  * **Partitioning:** By `transaction_date`. Scans only relevant days instead of full history.
  * **Clustering:** By `is_fraud`, `hour_of_day`. Sorts data physically to speed up filter queries.
  * **Incremental Loading:**
      * **Full Refresh:** 6-9 seconds (284k rows).
      * **Incremental:** \<1 second (Processing only new rows).
      * **Merge Strategy:** Uses BigQuery `MERGE` to update duplicates based on `transaction_id`.

### Data Quality Findings

  * **Zero-Dollar Transactions:** 1,825 rows found (0.64%). Confirmed as valid "Auth Checks." Updated tests to allow `$0.00` but block negative values.

-----

## 3\. Orchestration (Dagster)

### Asset-Based Design

Instead of "Tasks," we manage "Assets" (Tables).

  * **Ingestion Asset:** Python script loads CSV to BigQuery.
  * **Transformation Assets:** dbt models (auto-mapped via `dagster-dbt`).
  * **Lineage:** Python → Staging → Intermediate → Marts.

### Automation

  * **Daily Schedule:** 2:00 AM Singapore Time.
  * **Weekly Schedule:** Sunday 3:00 AM (Full Rebuild).
  * **Storage:** Uses **PostgreSQL 15** (via Docker) to persist run history. Replaced ephemeral SQLite to ensure logs survive container restarts.

-----

## 4\. Containerization (Docker)

### The "Factory" Model

  * **Image (The Blueprint):** Custom Python 3.11 image with `dagster`, `dbt`, and `git`. Built once.
  * **Container (The Machine):** Running instance of the image.
  * **Volumes (The Conveyor Belts):**
      * **Secrets:** Maps `~/.dbt/key.json` (Host) → `/tmp/google_key.json` (Container). **Read-Only**.
      * **Data:** Maps `./data` (Host) → `/opt/dagster/app/data` (Container). **Read-Only**.
      * **Persistence:** Maps `postgres_data` (Volume) → `/var/lib/postgresql/data`.

### Key Files

  * **`Dockerfile`**: Multi-stage build. Installs dependencies first (Caching), then copies code.
  * **`docker-compose.yml`**: Orchestrates Dagster (App) and Postgres (DB). Manages networking and health checks.
  * **`start.sh`**: Entrypoint script. Validates keys and compiles dbt manifest *before* starting the webserver.

-----

## 5\. CI/CD Pipeline

### GitHub Actions Workflows

1.  **CI (`ci.yml`)**:

      * **Trigger:** Pull Request.
      * **Checks:**
          * **Linting:** `pre-commit` (Black, Isort, Trailing Whitespace).
          * **Unit Tests:** `pytest` verifies Python logic.
          * **Data Tests:** `dbt test` verifies SQL logic.
      * **Mocking:** Uses a dummy `.env` file to simulate credentials during testing.

2.  **Deploy (`deploy.yml`)**:

      * **Trigger:** Push to `main`.
      * **Action:** Authenticates via GitHub Secrets and runs `dbt run` against the Production dataset.

-----

## 6\. Security & Compliance

### "Defense in Depth" Strategy

  * **Zero Trust:** No credentials stored in code. All keys injected via Environment Variables.
  * **Git Hygiene:** Strict `.gitignore` blocking `*.json`, `.env`, `logs/`, and `*.pyc`.
  * **Container Security:**
      * Secrets mounted as **Read-Only**.
      * Non-root user enforcement where possible.
      * `.dockerignore` prevents copying local secrets into the image build context.
  * **Least Privilege:** Service Account limited to `Data Editor` and `Job User`. Cannot delete datasets or modify IAM policies.

-----

### 📝 Author Notes

  * **Challenge:** Windows paths vs. Linux paths in Docker.
      * **Solution:** Standardized on Linux paths inside the container and used Docker Volumes to bridge the difference.
  * **Challenge:** dbt Manifest not found in Docker.
      * **Solution:** Added `dbt compile` to the `start.sh` script to generate a fresh manifest at runtime.

<!-- end list -->
