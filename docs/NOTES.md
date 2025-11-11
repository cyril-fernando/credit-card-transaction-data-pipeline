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

## What We Built

### 1. Enabled APIs

gcloud services enable bigquery.googleapis.com

text
**Why:** GCP services locked by default to prevent charges

### 2. Created 3 Datasets (Singapore)

bq mk --location=asia-southeast1 --dataset fraud_detection_raw
bq mk --location=asia-southeast1 --dataset fraud_detection_dev
bq mk --location=asia-southeast1 --dataset fraud_detection_prod


**Why:** Separate raw/dev/prod to prevent accidental data corruption

### 3. Created Service Account

gcloud iam service-accounts create dbt-fraud-detection


**Why:** dbt needs its own credentials (not your password)

### 4. Granted Permissions

dataEditor = create/edit tables
jobUser = run queries


**Why:** Least privilege - only what dbt needs

### 5. Downloaded Key File

gcloud iam service-accounts keys create ~/.dbt/fraud-detection-key.json


**Why:** dbt's "password" to login to BigQuery

---

## Key Concepts

**Dataset vs Table:**
- Dataset = Folder (schema)
- Table = File (actual data)

**Why Singapore?**
- PH → Singapore = 30ms
- PH → US = 250ms
- Faster queries, lower cost

**Service Account vs Personal:**
- Personal = you (human)
- Service = robot (automation)
- If key leaks, delete robot (don't change your password)

**Security:**
- Key file in `~/.dbt/` (not Git)
- Only dataEditor + jobUser roles (not Owner)

---

## Cost Reality

**Your 150MB dataset:**
- Storage: $0.003/month
- Queries: Free (under 1TB/month limit)
- Total project: $1-3 for everything

**Free tier:**
- $300 credits
- 10GB storage free/month
- 1TB queries free/month

---

## Status

- [x] GCP project configured
- [x] 3 BigQuery datasets (Singapore)
- [x] Service account + key file
- [ ] dbt setup (next)

---

*Last updated: Nov 11, 2025*