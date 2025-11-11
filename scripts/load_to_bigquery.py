"""Load credit card fraud data to BigQuery raw dataset."""
import pandas as pd
from google.cloud import bigquery
import os

# Configuration
PROJECT_ID = "total-compiler-477816-r3"
DATASET_ID = "fraud_detection_raw"
TABLE_ID = "transactions"
CSV_PATH = "data/raw/creditcard.csv"
KEYFILE_PATH = os.path.expanduser("~/.dbt/fraud-detection-key.json")

def load_data():
    """Load CSV to BigQuery."""
    print(f"🔄 Loading data from {CSV_PATH}...")
    
    # Set credentials
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = KEYFILE_PATH
    
    # Initialize BigQuery client
    client = bigquery.Client(project=PROJECT_ID)
    
    # Read CSV
    print("📖 Reading CSV file...")
    df = pd.read_csv(CSV_PATH)
    print(f"✓ Loaded {len(df):,} rows, {len(df.columns)} columns")
    
    # Define table reference
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
    
    # Configure load job
    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE",  # Overwrite if exists
        autodetect=True,  # Auto-detect schema
    )
    
    # Load to BigQuery
    print(f"⬆️  Uploading to {table_ref}...")
    job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
    job.result()  # Wait for completion
    
    # Verify
    table = client.get_table(table_ref)
    print(f"✅ Success! Loaded {table.num_rows:,} rows to BigQuery")
    print(f"📍 Table: {table_ref}")
    print(f"💾 Size: {table.num_bytes / 1024 / 1024:.2f} MB")

if __name__ == "__main__":
    load_data()
