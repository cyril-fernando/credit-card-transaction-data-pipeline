# Credit Card Transaction Pipeline

A learning project implementing a modern data engineering pipeline with dbt, BigQuery, Dagster, and GitHub Actions to process credit card transaction data.

## 🎓 Learning Outcomes

Through this project I learned:

- 🏗️ **Implementing medallion architecture with dbt**
  - Built 3-layer data transformation pipeline (Bronze → Silver → Gold)
  - Applied data modeling best practices

- ⚙️ **Setting up automated CI/CD pipelines**
  - Created GitHub Actions workflows for testing and deployment
  - Achieved 83-second test validation and 99-second deployments

- 🐳 **Containerizing data applications with Docker**
  - Multi-container orchestration with Docker Compose
  - Managed service dependencies (Dagster + PostgreSQL)

- 🔧 **Orchestrating workflows with Dagster**
  - Automated pipeline scheduling and monitoring
  - Implemented asset-based data lineage tracking

- ✅ **Writing comprehensive data quality tests**
  - Built 15 automated tests (11 dbt + 4 Python)
  - Achieved 100% test coverage with zero failures

- ☁️ **Working with BigQuery at scale**
  - Processed 284K+ transactions with 10,585 tx/sec throughput
  - Optimized query performance and cost ($0.26/year)

- 🔒 **Managing secrets and credentials securely**
  - Implemented GitHub Secrets for CI/CD
  - Applied least-privilege access principles

## Project Goals

Built to learn and practice:
- dbt transformations (3-layer medallion architecture)
- CI/CD automation (GitHub Actions)
- Container orchestration (Docker Compose)
- Data quality testing (dbt + pytest)
- Cloud data warehouse (BigQuery)

## Dataset

**Source:** [Kaggle Credit Card Fraud Detection](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud)
- 284,807 transactions
- 150 MB CSV file
- 30 anonymized features
- 492 fraudulent transactions (0.17%)

## Tech Stack

- **Language:** Python 3.11
- **Transformation:** dbt Core 1.10
- **Data Warehouse:** Google BigQuery
- **Orchestration:** Dagster 1.12
- **Database:** PostgreSQL (metadata)
- **Infrastructure:** Docker Compose
- **CI/CD:** GitHub Actions
- **Testing:** pytest, dbt tests

## Architecture
![Architecture](docs/architecture-batch-dagster-dbt-bigquery.png)

This project runs a containerised, batch data pipeline where:
- `creditcard.csv` is ingested and loaded into BigQuery staging tables.
- `dbt` transforms data through staging → intermediate → marts layers in BigQuery.
- `Dagster` (running in Docker) orchestrates the dbt runs and data loads.
- `GitHub Actions` builds the Docker image and runs dbt tests as part of CI/CD.
- Business intelligence tools and machine learning jobs consume the marts layer.

## Performance

See [BENCHMARK_RESULTS.md](BENCHMARK_RESULTS.md) for detailed metrics.

**Key Stats:**
- **Throughput:** 10,585 transactions/second
- **End-to-End:** 72 seconds (load + transform + test)
- **CI Test:** 83 seconds
- **Deploy:** 99 seconds
- **Test Coverage:** 100% (15/15 passing)
- **Cost:** $0.00075 per run

**vs Industry Standards:**
- 2-4x faster transformation (27s vs 45-120s typical)
- 83% faster deployment (99s vs 10-30 min manual)
- 99.99% lower cost ($0.26/year vs $2,400+ typical)

## Project Structure

```
fraud-detection-platform/
├── .github/workflows/
│   ├── ci.yml              # Test on pull requests
│   └── deploy.yml          # Deploy on push to main
├── dagster_project/
│   ├── fraud_detection_dagster/
│   │   ├── assets.py       # Dagster asset definitions
│   │   └── definitions.py  # Dagster job configuration
│   ├── Dockerfile          # Dagster container setup
│   └── dagster.yml         # Dagster storage config
├── dbt_project/
│   ├── models/
│   │   ├── staging/        # Layer 1: Data cleaning
│   │   ├── intermediate/   # Layer 2: Feature engineering
│   │   └── marts/          # Layer 3: Business logic
│   ├── tests/              # Custom SQL data quality tests
│   └── dbt_project.yml     # dbt configuration
├── scripts/
│   ├── download_data.py    # Download Kaggle dataset
│   └── load_to_bigquery.py # Load raw data to BigQuery
├── tests/
│   └── test_data_quality.py # Python unit tests (pytest)
├── docker-compose.yml      # Multi-container orchestration
├── .env.example            # Environment variable template
├── requirements.txt        # Python dependencies
└── BENCHMARK_RESULTS.md    # Performance metrics
```
Quick Start
Prerequisites

    Python 3.11+

    Docker & Docker Compose

    Google Cloud Platform account with BigQuery enabled

    Kaggle account (for dataset)

 1. Clone Repository

```
git clone https://github.com/cyril-fernando/credit-card-transaction-data-pipeline.git
cd credit-card-transaction-data-pipeline
```
 2. Set Up Environment


 Create virtual environment
`python -m venv venv`

 Activate (Windows)
`.\venv\Scripts\activate`

 Activate (Mac/Linux)
`source venv/bin/activate`

### Install dependencies
`pip install -r requirements.txt`

3. Configure Google Cloud

        Create GCP project

        Enable BigQuery API

        Create service account with roles:

        BigQuery Data Editor

        BigQuery Job User

        Download service account key JSON

        Save to ~/.dbt/fraud-detection-key.json

4. Download Data

          Visit Kaggle Credit Card Fraud Detection

          Download creditcard.csv

          Place in data/raw/ folder

5. Load Data to BigQuery


`python scripts/load_to_bigquery.py`

6. Run dbt Transformations

```
cd dbt_project
dbt deps
dbt run
dbt test
```
7. Start Dagster (Optional)


### Start containers
`docker compose up -d`

 Access Dagster UI at `http://localhost:3000`

###  Stop containers
`docker compose down`

Testing
`Run Python Tests`

bash
`pytest tests/ -v`

Run dbt Tests

```
cd dbt_project
dbt test
```
Test Coverage

    4 Python unit tests (data quality checks)

    11 dbt tests (3 custom SQL + 8 schema tests)

    Total: 15 tests with 100% pass rate

CI/CD Pipeline

    Automated Testing (ci.yml)

    Triggers on pull requests

    Runs dbt test to validate changes

    Blocks merge if tests fail

    Duration: 83 seconds

Automated Deployment (deploy.yml)

    Triggers on push to main

    Runs dbt run to update BigQuery tables

    Runs dbt test to verify deployment

    Duration: 99 seconds

Data Pipeline Details
dbt Models

Staging Layer (stg_raw_transactions.sql)

    Cleans raw transaction data

    Standardizes column names

    Handles data type conversions

Intermediate Layer (int_transaction_features.sql)

    Engineers features for fraud detection

    Calculates transaction velocity

    Aggregates historical patterns

Marts Layer (fraud_risk_scores.sql)

    Generates final fraud risk scores

    Applies business rules

    Outputs analytics-ready table

Data Quality Tests

    Transaction amounts must be positive

    Fraud rate must be realistic (0.1% - 2%)

    Transaction dates must be valid

    No duplicate transaction IDs

    No missing values in critical columns

Security Practices

    Service account uses least-privilege permissions

    Credentials stored in GitHub Secrets (not code)

    .gitignore excludes sensitive files

    Environment variables for configuration

    Docker volumes mounted as read-only where applicable

Future Improvements

    Add incremental models for larger datasets

    Implement data profiling and monitoring

    Add more sophisticated fraud detection features

    Set up alerting for data quality failures

    Optimize BigQuery costs with partitioning

Contributing

    Fork the repository

    Create feature branch (git checkout -b feature/amazing-feature)

    Commit changes (git commit -m 'Add amazing feature')

    Push to branch (git push origin feature/amazing-feature)

    Open Pull Request

# License

This project is for educational and portfolio purposes.
# Author

    Cyril Fernando

    GitHub: @cyril-fernando

Acknowledgments

    Dataset: Kaggle Credit Card Fraud Detection

    dbt Labs for transformation framework

    Dagster team for orchestration platform
