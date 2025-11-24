"""Basic data quality tests for fraud detection pipeline."""

from pathlib import Path

import pandas as pd
import pytest

CSV_PATH = Path("data/raw/creditcard.csv")


def require_csv() -> None:
    """
    Skip data-quality tests if the Kaggle CSV is not available.

    In local dev, place creditcard.csv under data/raw/ to run these tests.
    In CI, we intentionally do not ship the full dataset, so tests are skipped.
    """
    if not CSV_PATH.exists():
        pytest.skip(f"{CSV_PATH} not found; skipping data-quality tests")


def test_csv_exists() -> None:
    """Verify raw data file exists."""
    require_csv()
    assert CSV_PATH.exists(), "creditcard.csv not found in data/raw/"


def test_data_structure() -> None:
    """Verify CSV has expected columns."""
    require_csv()
    df = pd.read_csv(CSV_PATH)

    required_columns = ["Time", "Amount", "Class"]
    for col in required_columns:
        assert col in df.columns, f"Missing required column: {col}"


def test_fraud_rate() -> None:
    """Verify fraud rate is realistic (should be < 1%)."""
    require_csv()
    df = pd.read_csv(CSV_PATH)
    fraud_rate = df["Class"].mean()

    assert fraud_rate < 0.01, f"Fraud rate too high: {fraud_rate*100:.2f}%"
    assert fraud_rate > 0, "No fraud cases found"


def test_no_missing_values() -> None:
    """Verify no missing values in critical columns."""
    require_csv()
    df = pd.read_csv(CSV_PATH)

    assert df["Amount"].notna().all(), "Missing values in Amount column"
    assert df["Class"].notna().all(), "Missing values in Class column"
