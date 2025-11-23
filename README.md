
# Credit Card Transaction Pipeline

A modern, containerized data engineering pipeline that ingests, transforms, and analyzes credit card transaction data using dbt, BigQuery, Dagster, and Docker.

![CI/CD Status](https://img.shields.io/github/actions/workflow/status/cyril-fernando/credit-card-transaction-data-pipeline/ci.yml?style=flat-square&label=CI%20Build)
![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square)
![dbt](https://img.shields.io/badge/dbt-1.10-orange?style=flat-square)

## 🎓 Learning Outcomes

Through this project, I mastered the end-to-end data engineering lifecycle:

- **🏗️ Medallion Architecture:** Implemented a Bronze/Silver/Gold transformation layer using dbt to clean and model raw transaction data.
- **⚙️ CI/CD Automation:** Built GitHub Actions workflows that validate SQL syntax, run unit tests, and lint code in < 2 minutes.
- **🐳 Containerization:** Orchestrated a multi-container platform (Dagster + Postgres) using Docker Compose for reproducible environments.
- **🔧 Orchestration:** Automated asset materialization and dependency management using Dagster's software-defined assets.
- **✅ Data Quality:** Achieved 100% test coverage using Great Expectations and dbt schema tests to prevent bad data from entering the warehouse.
- **☁️ Cloud Engineering:** Managed IAM permissions, Service Accounts, and BigQuery datasets securely.

---

## 🏗️ Architecture

The pipeline follows a batch-processing model triggered by a daily schedule.

![Architecture Diagram](docs/architecture-batch-dagster-dbt-bigquery.png)

1. **Ingestion:** Python script loads raw CSV data (`creditcard.csv`) into BigQuery (`raw_transactions`).
2. **Transformation:** dbt transforms data through 3 layers:
   - **Staging:** Type casting, renaming, and basic cleaning.
   - **Intermediate:** Feature engineering (velocity, user history).
   - **Marts:** Final fraud risk scoring logic.
3. **Orchestration:** Dagster manages the dependency graph, ensuring dbt runs only after successful ingestion.
4. **Persistence:** A local Postgres container stores run history and logs.

---

## 🛠️ Tech Stack

| Component | Tool | Usage |
| :--- | :--- | :--- |
| **Language** | Python 3.11 | Ingestion logic & Orchestration definitions |
| **Transformation** | dbt Core 1.10 | SQL transformations & Data Modeling |
| **Warehouse** | Google BigQuery | Serverless Storage & Compute |
| **Orchestration** | Dagster 1.12 | Pipeline scheduling & Lineage tracking |
| **Infrastructure** | Docker Compose | Local container orchestration |
| **CI/CD** | GitHub Actions | Automated Testing & Linting |
| **Quality** | pytest / dbt test | Unit & Data Integrity testing |

---

## 🚀 Quick Start

### Prerequisites
* Docker Desktop installed & running.
* Google Cloud Service Account Key (`json`) with BigQuery Admin permissions.
* Kaggle Account (to download the dataset).

### 1. Clone Repository
```bash
git clone [https://github.com/cyril-fernando/credit-card-transaction-data-pipeline.git](https://github.com/cyril-fernando/credit-card-transaction-data-pipeline.git)
cd credit-card-transaction-data-pipeline
````

### 2\. Setup Configuration

Copy the template and update it with your Google Credentials.

```bash
cp .env.example .env
```

*Open `.env` and verify `DBT_KEY_PATH` points to your actual JSON key file.*

### 3\. Download Data

Download the [Kaggle Credit Card Fraud Detection](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud) dataset and save it to:
`data/raw/creditcard.csv`

### 4\. Launch the Platform

This command builds the custom Docker image and starts the Dagster & Postgres containers.

```bash
docker-compose up -d --build
```

### 5\. Access the UI

Open your browser to **[http://localhost:3000](https://www.google.com/search?q=http://localhost:3000)**.

  * Click **"Overview"** to see the pipeline lineage.
  * Click **"Materialize All"** to trigger a run.

-----

## 🧪 Testing & Quality

This project emphasizes "Defensive Engineering."

### Run Unit Tests (Logic Check)

```bash
docker-compose exec dagster pytest dagster_project/tests/
```

### Run Data Quality Tests (Data Check)

```bash
docker-compose exec dagster dbt test --project-dir dbt_project
```

### Coverage Metrics

  * **Unit Tests:** 4 (Import checks, Configuration validation)
  * **Data Tests:** 11 (Schema validation, Referential integrity, Custom SQL logic)
  * **Pass Rate:** 100%

-----

## 📂 Project Structure

```text
fraud-detection-platform/
├── .github/workflows/      # CI/CD Pipelines
├── dagster_project/        # Orchestration Logic
│   ├── assets.py           # Software-Defined Assets
│   └── definitions.py      # Pipeline Configuration
├── dbt_project/            # Transformation Logic
│   ├── models/             # SQL Models (Staging/Inter/Marts)
│   └── tests/              # Custom SQL Tests
├── docker-compose.yml      # Infrastructure Definition
├── Dockerfile              # Custom Image Definition
├── requirements.txt        # Python Dependencies
└── README.md               # You are here
```

-----

## 🛡️ Security Practices

  * **Least Privilege:** Service Accounts are scoped strictly to BigQuery datasets.
  * **Secret Management:** No credentials are stored in git. All keys are injected via Environment Variables.
  * **Docker Security:** Secrets are mounted as Read-Only (`:ro`) volumes to prevent container tampering.
  * **Ignore Rules:** Strict `.gitignore` and `.dockerignore` policies prevent accidental data leaks.

-----

## 🔮 Future Improvements

  * [ ] Migrate to **Incremental Models** for cost optimization on larger datasets.
  * [ ] Implement **Great Expectations** for deeper statistical profiling.
  * [ ] Add **Slack Alerts** for pipeline failures using Dagster Sensors.
  * [ ] Deploy to **GCP Cloud Run** for serverless production hosting.

-----

## 👤 Author

**Cyril Fernando**

  * GitHub: [@cyril-fernando](https://www.google.com/search?q=https://github.com/cyril-fernando)
  * Role: Data Engineer

*Built for educational and portfolio purposes.*
