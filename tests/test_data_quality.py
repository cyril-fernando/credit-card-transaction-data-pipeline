"""Basic data quality tests for fraud detection pipeline."""
import pandas as pd
from pathlib import Path


def test_csv_exists():
    """Verify raw data file exists."""
    csv_path = Path("data/raw/creditcard.csv")
    assert csv_path.exists(), "creditcard.csv not found in data/raw/"


def test_data_structure():
    """Verify CSV has expected columns."""
    df = pd.read_csv("data/raw/creditcard.csv")
    
    required_columns = ['Time', 'Amount', 'Class']
    for col in required_columns:
        assert col in df.columns, f"Missing required column: {col}"


def test_fraud_rate():
    """Verify fraud rate is realistic (should be < 1%)."""
    df = pd.read_csv("data/raw/creditcard.csv")
    fraud_rate = df['Class'].mean()
    
    assert fraud_rate < 0.01, f"Fraud rate too high: {fraud_rate*100:.2f}%"
    assert fraud_rate > 0, "No fraud cases found"


def test_no_missing_values():
    """Verify no missing values in critical columns."""
    df = pd.read_csv("data/raw/creditcard.csv")
    
    assert df['Amount'].notna().all(), "Missing values in Amount column"
    assert df['Class'].notna().all(), "Missing values in Class column"


if __name__ == "__main__":
    # Run all tests
    test_csv_exists()
    print("✅ CSV exists")
    
    test_data_structure()
    print("✅ Data structure valid")
    
    test_fraud_rate()
    print("✅ Fraud rate realistic")
    
    test_no_missing_values()
    print("✅ No missing values")
    
    print("\n✅ All tests passed!")
