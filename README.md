# Fraud Detection Data Platform

**Author:** Cyril Fernando  
**Status:** 🚧 Checkpoint 2 Complete → Starting dbt Setup

---

## 🎯 Goal

Build a production-grade fraud detection pipeline demonstrating modern data engineering stack for Philippine job market.

---

## 🛠️ Tech Stack

| Layer | Tool | Why |
|-------|------|-----|
| Cloud | GCP (Singapore) | Closest to PH, best pricing |
| Warehouse | BigQuery | Market leader, 5x bigger than competitors |
| Transformation | dbt Core | Industry standard (70% of DE jobs) |
| Orchestration | Dagster | Modern, asset-based |
| DevOps | Docker + Terraform | Containerization + IaC |
| CI/CD | GitHub Actions | Automated testing |

---

## 📊 Dataset

**Credit Card Fraud Detection** (284K transactions, 0.17% fraud rate)
- Real-world imbalanced data challenge
- Financial services domain (high demand in PH)

---

## 📁 Structure

```
fraud-detection-platform/
├── data/raw/              # Local dataset (150MB)
├── dbt_project/           # Transformation models
├── dagster_project/       # Orchestration
├── scripts/               # Python utilities
├── docs/notes.md          # Learning notes
└── tests/                 # Quality checks
```

---

## ✅ Progress

**Week 1: Foundation**
- [x] Local workspace setup
- [x] GCP project + BigQuery (Singapore)
- [x] Service account + IAM permissions
- [ ] dbt initialization ← **NEXT**
- [ ] Load data to BigQuery
- [ ] First transformation model

**Week 2-4:** Orchestration → Production → Documentation

---

## 🔐 Security

- Service account (not personal credentials)
- Least-privilege IAM (dataEditor + jobUser only)
- Credentials in ~/.dbt/ (excluded from Git)
- Budget alerts at $50 threshold

---

## 💰 Cost

**Expected:** $1-3 total (within $300 free credits)
- Storage: $0.003/month
- Queries: Free tier (1TB/month)

---

## 🌏 Architecture

```
CSV → Python Script → BigQuery Raw (Bronze)
         ↓
    dbt Transform
         ↓
Dev (Silver) + Prod (Gold)
         ↓
Dagster Orchestration
```

---

## 👤 Contact

GitHub: [@cyril-fernando](https://github.com/cyril-fernando)

---

*Data Engineering Portfolio | Philippines | 2025*