# Project Learning Notes

## GCP Setup Summary (Checkpoint 2)

### 🏢 The Office Building Analogy

**GCP Project** = Your rented office floor
- ID: `total-compiler-477816-r3`

**BigQuery** = Warehouse in your office
- Where data is stored and queried

**Datasets** = Sections of the warehouse
- `fraud_detection_raw` = Loading dock (raw data arrives)
- `fraud_detection_dev` = Workshop (you experiment)
- `fraud_detection_prod` = Showroom (final clean data)

**Service Account** = Robot employee
- Name: `dbt-fraud-detection@...`
- Has badge: `fraud-detection-key.json`
- Can only access warehouse (not your office)

**Region** = Building location
- `asia-southeast1` = Singapore (close to Philippines)

---

## What has been Built

# GCP Setup Guide - Fraud Detection Platform

# GCP Setup - Fraud Detection Platform

## Command 1: Login to GCP

```powershell
gcloud auth login
```

**What it does:** Opens browser for Google account login, saves authentication token to `C:\Users\cyfer\.config\gcloud\`

**Why:** GCP needs to verify WHO is running commands (like showing ID at building entrance)

**Behind the scenes:** Browser → Google login → Token generated → Saved locally → Future commands use token

---

## Command 2: Set Active Project

```powershell
gcloud config set project total-compiler-477816-r3
```

**What it does:** Sets default project for all future commands

**Why:** Prevents typing project ID in every command

**Alternative:**
```powershell
# Without default: gcloud iam service-accounts list --project=total-compiler-477816-r3
# With default: gcloud iam service-accounts list
```

---

## Command 3: Enable BigQuery API

```powershell
gcloud services enable bigquery.googleapis.com
```

**What it does:** Activates BigQuery service in your project

**Why disabled by default:** Cost protection, security, explicit opt-in required

**Verify:**
```powershell
gcloud services list --enabled --filter="name:bigquery"
```

---

## Command 4A: Create Raw Dataset

```powershell
bq mk --location=asia-southeast1 --dataset fraud_detection_raw
```

**Breaking it down:**
- `bq` = BigQuery command tool
- `mk` = "make" (create)
- `--location=asia-southeast1` = Store in Singapore
- `--dataset` = Creating dataset (not table)
- `fraud_detection_raw` = Dataset name

**Structure created:**
```
Project: total-compiler-477816-r3
  └── BigQuery
      └── fraud_detection_raw (dataset)
          └── [empty - no tables yet]
```

**Why this location:** Affects query speed, cost, data residency (can't change later)

---

## Command 4B-C: Create Dev and Prod Datasets

```powershell
bq mk --location=asia-southeast1 --dataset fraud_detection_dev
bq mk --location=asia-southeast1 --dataset fraud_detection_prod
```

**Why separate datasets:**

❌ **Bad (single dataset):**
```
fraud_detection
  ├── raw_transactions
  ├── test_cyfer_experiment_v3 (mess)
  ├── final_report (business sees this)
  └── temp_table_delete_later (oops)
```

✅ **Good (separate datasets):**
```
fraud_detection_raw → Original data (untouched)
fraud_detection_dev → Your sandbox (break things safely)
fraud_detection_prod → Production (tested and clean)
```

---

## Command 5: Verify Datasets

```powershell
bq ls
```

**Expected output:**
```
  datasetId
 -----------------------
  fraud_detection_raw
  fraud_detection_dev
  fraud_detection_prod
```

---

## Command 6: Create Service Account

```powershell
gcloud iam service-accounts create dbt-fraud-detection --display-name="dbt Fraud Detection"
```

**What gets created:**
- Email: `dbt-fraud-detection@total-compiler-477816-r3.iam.gserviceaccount.com`
- Type: Service account (robot user)
- Permissions: NONE yet (blank slate)

**Why "dbt-fraud-detection":** Describes purpose (dbt tool) + project (fraud detection)

---

## Command 7: Grant BigQuery Data Editor Role

```powershell
gcloud projects add-iam-policy-binding total-compiler-477816-r3 \
  --member="serviceAccount:dbt-fraud-detection@total-compiler-477816-r3.iam.gserviceaccount.com" \
  --role="roles/bigquery.dataEditor"
```

**What "dataEditor" includes:**

✅ **CAN:**
- Create tables
- Insert/update/delete data
- Read data
- Delete tables
- Update schemas

❌ **CANNOT:**
- Create/delete datasets
- Manage IAM permissions
- View billing

---

## Command 8: Grant BigQuery Job User Role

```powershell
gcloud projects add-iam-policy-binding total-compiler-477816-r3 \
  --member="serviceAccount:dbt-fraud-detection@total-compiler-477816-r3.iam.gserviceaccount.com" \
  --role="roles/bigquery.jobUser"
```

**What "jobUser" includes:**
- Submit query jobs (run SELECT)
- Get job status
- Cancel own jobs

**Why TWO roles needed:**

Think of warehouse access:
- `dataEditor` = Key to warehouse (can enter, move boxes)
- `jobUser` = Permission to use forklift (can execute work)

Need BOTH:
- Without `dataEditor`: Can start forklift, but door locked
- Without `jobUser`: Can open door, but forklift won't start

---

## Command 9: Create .dbt Folder

```powershell
New-Item -ItemType Directory -Path $HOME\.dbt -Force
```

**What will go here:**
```
C:\Users\cyfer\.dbt\
  ├── fraud-detection-key.json (service account key)
  ├── profiles.yml (dbt connection config)
  └── logs/ (dbt run logs)
```

**Why outside project folder:** Credentials shouldn't be in Git

---

## Command 10: Download Service Account Key

```powershell
gcloud iam service-accounts keys create $HOME\.dbt\fraud-detection-key.json \
  --iam-account=dbt-fraud-detection@total-compiler-477816-r3.iam.gserviceaccount.com
```

**What happens:**
1. GCP generates RSA key pair (public + private)
2. Public key: Stored in GCP (verifies signatures)
3. Private key: Downloaded to your computer (signs requests)

**JSON file contains:**
```json
{
  "type": "service_account",
  "project_id": "total-compiler-477816-r3",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...",
  "client_email": "dbt-fraud-detection@total-compiler-477816-r3.iam.gserviceaccount.com"
}
```

**Security:** This file = password for service account. NEVER commit to Git.

**How dbt uses it:**
1. dbt reads `private_key` from JSON
2. dbt signs API request with private key
3. Sends signed request to BigQuery
4. BigQuery verifies signature
5. If valid, grants access

---

## Command 11: Verify Service Account

```powershell
gcloud iam service-accounts list --filter="email:dbt-fraud-detection*"
```

**Expected output:**
```
DISPLAY NAME         EMAIL                              DISABLED
dbt Fraud Detection  dbt-fraud-detection@...           False
```

---

## Command 12: Verify Key File

```powershell
Test-Path $HOME\.dbt\fraud-detection-key.json
```

**Should return:** `True`

---

## Key Concepts Summary

### Service Account = Robot Worker
- Has email address (identity)
- Has key file (password)
- Works 24/7, no human login needed

### IAM Roles = Permissions
- `dataEditor` = Create/modify tables
- `jobUser` = Run SQL queries
- Need BOTH for dbt to work

### Datasets = Folders
- `raw` = Original untouched data
- `dev` = Your sandbox
- `prod` = Final clean data

### Region = Physical Location
- `asia-southeast1` = Singapore
- Affects speed and cost
- Can't change after creation

---

## Quick Reference

```powershell
# Login
gcloud auth login
gcloud config set project total-compiler-477816-r3

# Create datasets
bq mk --location=asia-southeast1 --dataset fraud_detection_raw
bq mk --location=asia-southeast1 --dataset fraud_detection_dev
bq mk --location=asia-southeast1 --dataset fraud_detection_prod

# Create service account
gcloud iam service-accounts create dbt-fraud-detection --display-name="dbt Fraud Detection"

# Grant permissions
gcloud projects add-iam-policy-binding total-compiler-477816-r3 \
  --member="serviceAccount:dbt-fraud-detection@total-compiler-477816-r3.iam.gserviceaccount.com" \
  --role="roles/bigquery.dataEditor"

gcloud projects add-iam-policy-binding total-compiler-477816-r3 \
  --member="serviceAccount:dbt-fraud-detection@total-compiler-477816-r3.iam.gserviceaccount.com" \
  --role="roles/bigquery.jobUser"

# Download key
mkdir $HOME\.dbt -Force
gcloud iam service-accounts keys create $HOME\.dbt\fraud-detection-key.json \
  --iam-account=dbt-fraud-detection@total-compiler-477816-r3.iam.gserviceaccount.com

# Verify
bq ls
gcloud iam service-accounts list --filter="email:dbt-fraud-detection*"
Test-Path $HOME\.dbt\fraud-detection-key.json
```

# dbt Setup Notes


### Project Structure

```dbt_project/
├── models/
│ ├── staging/ (stg_) - Clean raw data, no business logic
│ ├── intermediate/ (int_) - Derived features, no aggregations
│ └── marts/ (fact_, dim_) - Optimized for business users
└── tests/ Custom SQL tests for business rules
```


### Key Learnings

**Materialization Strategy:**
- Staging/Intermediate: VIEWs (fast rebuilds, always fresh)
- Marts: TABLEs (fast queries, partitioned/clustered)

**Testing Philosophy:**
- Test data hygiene (unique, not_null on keys)
- Test business logic (positive amounts, fraud rate sanity checks)
- Test date ranges (catch calculation errors)
- Avoid over-testing (slow CI/CD, maintenance burden)

**Feature Engineering:**
- Z-scores: Detect outliers (amount_z > 3 = suspicious)
- Log transforms: Compress wide ranges for ML models
- Time features: hour_of_day, day_of_week for pattern detection

**BigQuery Optimization:**
- Partitioning: Vertical slicing by date (scan only needed days)
- Clustering: Horizontal sorting by common filters (is_fraud, hour_of_day)
- Cost: ~$0.04/month for 284K rows (negligible for portfolio)

**Environment Management:**
- profiles.yml controls dev vs prod datasets
- target: dev (default) → fraud_detection_dev
- target: prod → fraud_detection_prod
- Switch at runtime: dbt run --target prod

**Documentation:**
- dbt docs generate → Creates interactive website
- Shows lineage graph (DAG of models)
- Column-level descriptions for business users
- Essential for portfolio (proves communication skills)

**Data Quality Discovery:**
- Found 1,825 zero-dollar transactions (0.64% of dataset)
- These are valid authorization checks (verify card without charging)
- Updated test to allow zeros, block only negatives
- Learning: Real-world credit card data includes $0 auth checks

**Final State (Checkpoint 7):**
- 3 models built (staging → intermediate → marts)
- 20 tests passing (17 schema + 3 custom business logic)
- Full documentation with descriptions
- Lineage graph visualized
- Ready for orchestration (Dagster)

*Last updated: Nov 12, 2025*