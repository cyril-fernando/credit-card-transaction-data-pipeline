"""
Dagster asset definitions for credit card fraud detection pipeline.

Defines two asset layers:
1. Ingestion: Loads local CSV into BigQuery raw table
2. Transformation: Runs dbt models to create staging and mart tables
"""

import os
from pathlib import Path

import pandas as pd
from dagster import AssetExecutionContext, MaterializeResult, MetadataValue, asset
from dagster_dbt import DbtCliResource, DbtProject, dbt_assets
from dotenv import load_dotenv
from google.cloud import bigquery

load_dotenv()


# ============================================================================
# CONFIGURATION
# ============================================================================

# Data source and BigQuery target configuration
CSV_PATH = os.getenv("CSV_PATH", "data/raw/creditcard.csv")
BQ_DATASET = os.getenv("BQ_DATASET_ID", "fraud_detection_raw")
BQ_TABLE = os.getenv("BQ_TABLE_ID", "transactions")
KEYFILE_PATH = os.getenv("DBT_KEY_PATH")
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")

# dbt project paths - defaults to standard locations if env vars not set
DBT_PROJECT_DIR = Path(
    os.getenv("DBT_PROJECT_DIR", str(Path(__file__).parent.parent.parent / "dbt_project"))
).resolve()

DBT_PROFILES_DIR = Path(os.getenv("DBT_PROFILES_DIR", str(Path.home() / ".dbt"))).resolve()

# dbt project connection object - used by dbt_assets decorator
dbt_project = DbtProject(
    project_dir=DBT_PROJECT_DIR,
    profiles_dir=DBT_PROFILES_DIR,
)


# ============================================================================
# ASSETS - INGESTION LAYER
# ============================================================================


@asset(
    key_prefix=["kaggle_raw"],
    name="transactions",
    group_name="ingestion",
)
def raw_transactions_table(context: AssetExecutionContext):
    """
    Loads creditcard.csv into BigQuery raw table.

    Reads local CSV and uploads to BigQuery using WRITE_TRUNCATE mode
    (full refresh - replaces table). Returns metadata for run history.
    """
    # Defensive check - fail fast if file missing
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"CSV not found at {CSV_PATH}")

    context.log.info(f"Reading CSV from {CSV_PATH}")
    try:
        df = pd.read_csv(CSV_PATH)
        row_count = len(df)
    except Exception as e:
        context.log.error(f"Failed to read CSV: {str(e)}")
        raise

    # Set GCP authentication if keyfile provided
    if KEYFILE_PATH:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = KEYFILE_PATH

    try:
        client = bigquery.Client(project=GCP_PROJECT_ID)
        table_id = f"{GCP_PROJECT_ID}.{BQ_DATASET}.{BQ_TABLE}"

        job_config = bigquery.LoadJobConfig(
            write_disposition="WRITE_TRUNCATE",
            autodetect=True,
        )
        context.log.info(f"Uploading {row_count:,} rows to {table_id}")
        job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
        job.result()
        context.log.info("Upload completed successfully")

    except Exception as e:
        context.log.error(f"BigQuery operation failed for {table_id}: {str(e)}")
        raise

    return MaterializeResult(
        metadata={
            "row_count": row_count,
            "table_id": table_id,
            "preview": MetadataValue.md(df.head().to_markdown()),
        }
    )


# ============================================================================
# ASSETS - TRANSFORMATION LAYER (dbt)
# ============================================================================


@dbt_assets(manifest=dbt_project.manifest_path)
def credit_card_dbt_assets(context: AssetExecutionContext, dbt: DbtCliResource):
    """
    Exposes all dbt models as Dagster assets.

    Runs dbt build command to execute models and tests in dependency order.
    Each dbt model appears as an asset in the Dagster UI via manifest discovery.
    """
    yield from dbt.cli(["build"], context=context).stream()
