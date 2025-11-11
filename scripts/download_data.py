import pandas as pd
from pathlib import Path
import shutil

# Source file location
source = Path(r"D:\vs_code_projs\kaggle_data\creditcard.csv")

# Check if source exists
if not source.exists():
    print(f"❌ File not found: {source}")
    print("Please verify the file path")
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
