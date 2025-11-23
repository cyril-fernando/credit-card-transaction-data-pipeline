"""
load_to_bigquery.py

Purpose:
Loads validated creditcard.csv from data/raw/ into a configured BigQuery table,
using environment variables for all credentials and resource identifiers. Includes
defensive configuration checks, robust error handling, and post-upload reporting.
"""

import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from google.cloud import bigquery

# Load environment variables
load_dotenv()

# Defensive configuration: require all critical env vars to be set and valid
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
DATASET_ID = os.getenv("BQ_DATASET_ID")
TABLE_ID = os.getenv("BQ_TABLE_ID")
CSV_PATH = os.getenv("CSV_PATH")
KEYFILE_PATH = os.getenv("DBT_KEY_PATH")

missing_vars = []
for var, val in [
    ("GCP_PROJECT_ID", PROJECT_ID),
    ("BQ_DATASET_ID", DATASET_ID),
    ("BQ_TABLE_ID", TABLE_ID),
    ("CSV_PATH", CSV_PATH),
    ("DBT_KEY_PATH", KEYFILE_PATH),
]:
    if not val:
        missing_vars.append(var)
if missing_vars:
    raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

if not Path(CSV_PATH).exists():
    raise FileNotFoundError(f"CSV file not found at path: {CSV_PATH}")
if not Path(KEYFILE_PATH).exists():
    raise FileNotFoundError(f"GCP keyfile not found at path: {KEYFILE_PATH}")


def load_to_bigquery():
    print(f"Loading CSV: {CSV_PATH} to BigQuery table {PROJECT_ID}.{DATASET_ID}.{TABLE_ID}")

    try:
        # Authenticate using service account key
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = KEYFILE_PATH
        client = bigquery.Client(project=PROJECT_ID)

        # Read CSV data
        print("Reading CSV file...")
        df = pd.read_csv(CSV_PATH)
        print(f"Loaded {len(df):,} rows, {len(df.columns)} columns.")

        # Configure table reference and BigQuery load job
        table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
        job_config = bigquery.LoadJobConfig(
            write_disposition="WRITE_TRUNCATE",
            autodetect=True,
        )

        # Upload data to BigQuery and wait for completion
        print(f"Uploading to BigQuery table {table_ref}...")
        job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
        job.result()
        print("Upload succeeded.")

        # Post-upload summary and metadata
        table = client.get_table(table_ref)
        print(f"Rows loaded: {table.num_rows:,}")
        print(f"Table: {table_ref}")
        print(f"Size: {table.num_bytes / 1024 / 1024:.2f} MB.")
    except Exception as e:
        import traceback

        print(f"Upload failed: {e}")
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    load_to_bigquery()
