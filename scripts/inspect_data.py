import pandas as pd
from pathlib import Path

DATA_PATH = Path("data/raw/twcs.csv")

print("=" * 60)
print("SUPPORTLENS - DATASET INSPECTION")
print("=" * 60)

df = pd.read_csv(DATA_PATH)

print("\nShape:")
print(df.shape)

print("\nColumns:")
for col in df.columns:
    print(" -", col)

print("\nFirst 5 rows:")
print(df.head())

print("\nMissing values:")
print(df.isnull().sum())

print("\nInbound distribution:")
print(df["inbound"].value_counts(dropna=False))

print("\nUnique authors:")
print(df["author_id"].nunique())

print("\nUnique tweet IDs:")
print(df["tweet_id"].nunique())