"""
download_data.py

Purpose:
Ensures the creditcard.csv dataset is present in data/raw/, copying it from KAGGLE_DATA_PATH if set,
or validating its presence locally. Includes defensive configuration checks, robust error handling,
and summary statistics for data validation.
"""

import os
import shutil
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()


def download_data():
    # Defensive check for required environment variable
    kaggle_path = os.getenv("KAGGLE_DATA_PATH")
    if not kaggle_path:
        raise EnvironmentError("KAGGLE_DATA_PATH must be set in your environment (.env file or OS)")

    # Compose source file path and validate existence
    source = Path(kaggle_path) / "creditcard.csv"
    if not source.exists():
        raise FileNotFoundError(
            f"Source file not found at {source.absolute()}.\n"
            "Add KAGGLE_DATA_PATH to .env or place creditcard.csv in the correct folder."
        )

    # Prepare destination and ensure raw data folder exists
    output = Path("data/raw/creditcard.csv")
    output.parent.mkdir(parents=True, exist_ok=True)

    # Copy data file and validate result
    try:
        if source.resolve() != output.resolve():
            shutil.copy(source, output)
            print(f"File copied to {output.absolute()}.")

        df = pd.read_csv(output)
    except Exception as e:
        print(f"File copy or CSV read failed: {e}")
        exit(1)

    # Print basic validation statistics
    print(f"Loaded {len(df):,} rows and {len(df.columns)} columns.")
    print(f"File size: {output.stat().st_size / 1024 / 1024:.2f} MB.")
    if "Class" in df.columns:
        print(f"Fraud rate: {df['Class'].mean() * 100:.2f}%")
    else:
        print("Warning: 'Class' column not found; can't compute fraud rate.")


if __name__ == "__main__":
    download_data()
