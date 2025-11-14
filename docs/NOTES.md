Project Learning Notes

Table of Contents

    GCP Setup

    dbt Models

    Dagster Orchestration

    Incremental Loading

    Docker Containerization

# GCP Setup
### The Office Building Analogy

GCP Project = Your rented office floor

    ID: total-compiler-477816-r3

BigQuery = Warehouse in your office

    Where data is stored and queried

Datasets = Sections of the warehouse

    fraud_detection_raw = Loading dock (raw data arrives)

    fraud_detection_dev = Workshop (you experiment)

    fraud_detection_prod = Showroom (final clean data)

Service Account = Robot employee

    Name: dbt-fraud-detection@...

    Has badge: fraud-detection-key.json

    Can only access warehouse (not your office)

Region = Building location

    asia-southeast1 = Singapore (close to Philippines)


# Setup Commands


## Login
    gcloud auth login
    gcloud config set project total-compiler-477816-r3

## Create datasets
    bq mk --location=asia-southeast1 --dataset fraud_detection_raw
    bq mk --location=asia-southeast1 --dataset fraud_detection_dev
    bq mk --location=asia-southeast1 --dataset fraud_detection_prod

## Create service account
    gcloud iam service-accounts create dbt-fraud-detection --display-name="dbt Fraud Detection"

## Grant permissions
    gcloud projects add-iam-policy-binding total-compiler-477816-r3 \
      --member="serviceAccount:dbt-fraud-detection@total-compiler-477816-r3.iam.gserviceaccount.com" \
      --role="roles/bigquery.dataEditor"

    gcloud projects add-iam-policy-binding total-compiler-477816-r3 \
      --member="serviceAccount:dbt-fraud-detection@total-compiler-477816-r3.iam.gserviceaccount.com" \
      --role="roles/bigquery.jobUser"

## Download key
    mkdir $HOME\.dbt -Force
    gcloud iam service-accounts keys create $HOME\.dbt\fraud-detection-key.json \
      --iam-account=dbt-fraud-detection@total-compiler-477816-r3.iam.gserviceaccount.com

    Key Concepts

    Service Account = Robot worker with email and key file, works 24/7

## IAM Roles = Permissions

    dataEditor = Create/modify tables

    jobUser = Run SQL queries

    Need BOTH for dbt to work 
    Datasets = Folders separating raw, dev, and prod environments
    Region = Physical location (can't change after creation)

# dbt Models
### Project Structure

```
dbt_project/
├── models/
│   ├── staging/ (stg_) - Clean raw data, no business logic
│   ├── intermediate/ (int_) - Derived features, no aggregations
│   └── marts/ - Optimized for business users
└── tests/ - Custom SQL tests for business rules
```

Materialization Strategy

    Staging/Intermediate: VIEWs (fast rebuilds, always fresh)

    Marts: TABLEs (fast queries, partitioned/clustered)

Feature Engineering

    Z-scores: Detect outliers (amount_z > 3 = suspicious)

    Log transforms: Compress wide ranges for ML models

    Time features: hour_of_day, day_of_week for pattern detection

BigQuery Optimization

    Partitioning: Vertical slicing by date (scan only needed days)

    Clustering: Horizontal sorting by common filters (is_fraud, hour_of_day)

    Cost: ~$0.04/month for 284K rows

Testing Philosophy

    Test data hygiene (unique, not_null on keys)

    Test business logic (positive amounts, fraud rate sanity checks)

    Test date ranges (catch calculation errors)

    Avoid over-testing (slows CI/CD)

Data Quality Discovery

    Found 1,825 zero-dollar transactions (0.64% of dataset)

    These are valid authorization checks (verify card without charging)

    Updated test to allow zeros, block only negatives

# Dagster Orchestration
### Project Structure

```
dagster_project/
├── fraud_detection_dagster/
│   ├── assets.py - Wraps dbt models as Dagster assets
│   └── definitions.py - Registers assets, jobs, schedules, sensors
├── pyproject.toml
└── setup.py
```
Asset-Based Orchestration

    dbt models wrapped as Dagster assets (stg → int → marts)

    Dependencies auto-mapped from dbt ref() functions

    Visual lineage graph in UI

Automation Patterns

    Daily schedule (2am): Incremental refresh of fraud scores

    Weekly schedule (Sunday 3am): Full rebuild for data quality

    Sensor (every 5min): Event-driven trigger when 6+ hours since last run

    Cron expressions: 0 2 * * * = 2am daily, 0 3 * * 0 = 3am Sundays

Jobs vs Schedules vs Sensors

    Job = What to run (groups assets into executable unit)

    Schedule = When to run it (timer/calendar)

    Sensor = Why to run it (event/condition)

Sensor Cursors

    Persistent storage between evaluations (sensors are stateless)

    Track "last run time" to check freshness thresholds

    Use context.cursor to read, context.update_cursor() to write

Cost Management

    Each run costs ~$0.0014 in BigQuery queries

    Daily automation: ~$0.042/month (30 days × $0.0014)

    Local Dagster: Free (no cloud hosting costs)

Configuration

    DBT_PROFILES_DIR: Points to C:\Users\cyfer\.dbt (credentials)

    execution_timezone: Asia/Singapore (ensures 2am local time)

    AssetSelection.all(): Runs all 3 assets together

# Incremental Loading
Why Added

    Current approach rebuilds entire table (284K rows) on every run

    Production pattern: Only process new data since last run

    Cost optimization: 90%+ reduction in data scanned and compute time

    Scalability: Solution works with 10M+ rows without performance degradation

Implementation

    Modified fraud_risk_scores.sql to use materialized='incremental'

    Added unique key (transaction_id) for duplicate handling

    Configured merge strategy (inserts new + updates existing)

    Conditional filter: WHERE transaction_date > MAX(existing_date) only applies on incremental runs

Incremental vs Full Refresh

    Full refresh: Drops table, rebuilds from scratch (all 284K rows)

    Incremental: Processes only new rows since last run (0 rows for static dataset)

    First run always full refresh (builds foundation), subsequent runs incremental

    Use --full-refresh flag to force complete rebuild when logic changes

Merge Strategy

    Uses BigQuery MERGE operation (INSERT new + UPDATE duplicates)

    Handles late-arriving data and reprocessing scenarios

    Alternative strategies: append (no dedup), insert_overwrite (partition replacement)

Performance Metrics

    Full refresh: 284.8K rows processed, 6.5 MiB scanned, ~6-9 seconds

    Incremental run: 0 rows processed, 2.2 MiB scanned, ~9 seconds (checking only)

    Production scenario with daily new data: 99% faster builds, 99% cost reduction

Configuration Details

    unique_key='transaction_id': Prevents duplicates

    partition_by: Enables date-based filtering (already configured)

    cluster_by: Sorts within partitions (already configured)

    on_schema_change='append_new_columns': Future-proofs schema evolution

Docker Containerization
Why Added

    Enable one-command deployment (docker compose up)

    Isolate dependencies and environment from host machine

    Demonstrate DevOps/containerization skills for modern data engineering roles

    Provide portable setup for portfolio reviewers

    Persist Dagster metadata across container restarts (run history, schedules, sensors)

Container Mental Model

    Container = Isolated mini-computer inside laptop with own filesystem, processes, network

    Image = Frozen snapshot/blueprint created from Dockerfile during docker build

    Volume = Persistent storage that survives container deletion (used for PostgreSQL data)

    Port Mapping = Tunnel between laptop and container (format: laptop_port:container_port)

Dockerfile vs docker-compose.yml

    Dockerfile: Recipe to BUILD one custom image (contains: FROM, WORKDIR, COPY, RUN, CMD)

    docker-compose.yml: Coordinator to RUN multiple containers together (orchestrates services, networks, volumes)

Multi-Container Architecture

    PostgreSQL 15: Stores Dagster run history and metadata with persistent volume (survives restarts)

    Dagster (custom): Runs orchestration layer with Python 3.13, dbt, auto-generates manifest.json on startup

    Both containers communicate via docker-compose networking, accessible at localhost:3000

Files Created

    dagster_project/Dockerfile - Recipe to build Dagster image

    docker-compose.yml - Orchestrates both containers

    .dockerignore - Excludes unnecessary files from builds

    requirements-docker.txt - Linux-compatible dependencies (no pywin32)

    profiles-docker.yml - dbt config with container paths

    dagster.yaml - Configures PostgreSQL for Dagster storage

Docker Commands

    # Start everything
    docker compose up -d

    # View logs
    docker compose logs -f dagster

    # Stop everything
    docker compose down

    # Rebuild after code changes
    docker compose build

    # Enter container
    docker compose exec dagster bash
    
## CI/CD Pipeline with GitHub Actions

### Workflows Implemented

**1. CI Workflow (`.github/workflows/ci.yml`)**
- **Trigger:** Pull requests to main branch
- **Purpose:** Validate code changes before merging
- **Actions:** Runs `dbt test` to ensure data quality checks pass
- **Prevents:** Broken code from reaching production

**2. Deploy Workflow (`.github/workflows/deploy.yml`)**
- **Trigger:** Pushes to main branch (automatic) or manual dispatch
- **Purpose:** Deploy dbt models to BigQuery
- **Actions:** 
  - Installs Python dependencies
  - Authenticates with GCP using service account
  - Runs `dbt deps`, `dbt run`, `dbt test`
- **Result:** Updates BigQuery tables with latest transformations

### Secrets Configuration
- **GCP_SA_KEY:** BigQuery service account key stored as GitHub repository secret
- **Access:** Settings → Secrets and variables → Actions
- **Security:** Never exposed in logs, only accessible to workflows

### Testing the Pipeline

Make a change and push
```
git checkout -b feature/test-change
echo "# Test" >> README.md
git add README.md
git commit -m "Test CI/CD"
git push -u origin feature/test-change
Create PR on GitHub → CI workflow runs automatically
```
---

## Final Project Summary

### Technologies Mastered
- **Cloud:** Google Cloud Platform, BigQuery
- **Data Transformation:** dbt, SQL, Python (pandas)
- **Orchestration:** Dagster, Docker Compose
- **CI/CD:** GitHub Actions
- **Database:** PostgreSQL
- **Testing:** pytest, dbt tests
- **Version Control:** Git, GitHub

### Professional Practices Demonstrated
1. **Security:** Service accounts, secrets management, .gitignore
2. **Portability:** Environment variables, Docker, cross-platform scripts
3. **Testing:** 11 automated tests (Python + dbt)
4. **Documentation:** README, code comments, clear commit messages
5. **Version Control:** Git workflow, branching strategy
6. **CI/CD:** Automated testing and deployment

## Summary of Security Measures Taken

### 1. Credential Protection
- **Removed from Git tracking:** `profiles-docker.yml` (contained Databricks token), `logs/dbt.log`
- **Added to .gitignore:** `*.json`, `.env`, `profiles.yml`, `profiles-docker.yml`, `logs/`
- **Verified exclusion:** Service account key (`fraud-detection-key.json`) never committed

### 2. Cross-Platform Compatibility
- **Created `.env` file:** Stores local-specific paths (LOCAL machine only, not committed)
- **Created `.env.example`:** Template for others to copy and customize
- **Updated `docker-compose.yml`:** Changed hardcoded `C:\Users\cyfer\` to `${DBT_KEY_PATH}` environment variable
- **Benefit:** Project now works on Windows, Mac, and Linux without code changes

### 3. Docker Security
- **Local-only passwords:** `dagster_password` in `docker-compose.yml` is safe (localhost-only, not exposed to internet)
- **Mounted credentials:** Key file mounted as read-only volume, not baked into Docker image
- **Persistent volume excluded:** `postgres_data/` in .gitignore (contains local database, not needed in repo)

### 4. Code Security Scan Results
- ✅ No API tokens, secrets, or private keys in tracked files
- ✅ No Windows-specific paths (removed `C:\Users\cyfer`)
- ✅ Only configuration variable names found (e.g., `POSTGRES_PASSWORD:`, `keyfile:`), not actual values
- ✅ Service account uses least-privilege permissions (`bigquery.dataEditor`, `bigquery.jobUser` only)

### 5. Files Properly Excluded
**What's in .gitignore:**
- Python artifacts: `venv/`, `__pycache__/`, `*.pyc`
- Credentials: `*.json`, `.env`, `profiles.yml`
- Generated files: `dbt_project/target/`, `logs/`
- Docker volumes: `postgres_data/`

**What's committed (safe):**
- Source code: `*.py`, `*.sql`, `*.yml`
- Templates: `.env.example`
- Documentation: `README.md`, `NOTES.md`
- Configuration: `docker-compose.yml` (with environment variables, no secrets)

---
## Security & Portability Setup

### Security Measures Implemented

**Credential Protection:**
- All secrets excluded from Git via comprehensive .gitignore
- Service account key never committed (stored in `~/.dbt/`, excluded by `*.json`)
- Removed accidentally tracked files: `profiles-docker.yml` (had Databricks token), `logs/dbt.log`
- Docker passwords are local-only (not exposed to internet)

**Cross-Platform Compatibility:**
- Created `.env` file for machine-specific configuration (not committed)
- Created `.env.example` template for other developers
- Replaced hardcoded Windows paths (`C:\Users\cyfer\`) with environment variables (`${DBT_KEY_PATH}`)
- Project now works on Windows, Mac, and Linux without code modification

**Service Account Least Privilege:**
- Only granted necessary BigQuery permissions: `dataEditor` + `jobUser`
- Cannot create/delete datasets, manage IAM, or access billing
- Credentials mounted as read-only volumes in Docker (not baked into images)

**Verification Performed:**
- Scanned all tracked files for secrets, tokens, API keys (clean)
- Confirmed no Windows-specific paths in committed code
- Verified .gitignore properly excludes credentials and generated files
- Tested `.env` properly ignored by Git

Last updated: November 14, 2025