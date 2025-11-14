import pandas as pd
from pathlib import Path
import shutil
import os
from dotenv import load_dotenv  # Add this

# Load environment variables from .env file
load_dotenv()  # Add this


def download_data():
    """
    Copy Kaggle credit card data to project folder.
    
    Setup:
    1. Download creditcard.csv from Kaggle
    2. Set KAGGLE_DATA_PATH in .env file
    """
    
    # Try environment variable
    kaggle_path = os.getenv("KAGGLE_DATA_PATH")
    
    if kaggle_path:
        source = Path(kaggle_path) / "creditcard.csv"
    else:
        # Fallback: assume it's already in data/raw/
        source = Path("data/raw/creditcard.csv")
    
    # Check if source exists
    if not source.exists():
        print("❌ File not found!")
        print("\nOptions:")
        print("1. Add to .env file: KAGGLE_DATA_PATH=C:/path/to/kaggle/data")
        print("2. Place creditcard.csv in data/raw/ folder")
        print(f"\nLooked for: {source.absolute()}")
        exit(1)
    
    # Destination
    output = Path("data/raw/creditcard.csv")
    output.parent.mkdir(parents=True, exist_ok=True)
    
    # Copy file
    print(f"Copying from: {source}")
    shutil.copy(source, output)
    
    # Verify
    df = pd.read_csv(output)
    print(f"✅ Copied {len(df):,} transactions")
    print(f"✅ Fraud rate: {df['Class'].mean()*100:.2f}%")
    print(f"✅ File size: {output.stat().st_size / 1024 / 1024:.2f} MB")


if __name__ == "__main__":
    download_data()
