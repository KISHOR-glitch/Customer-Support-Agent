import pandas as pd
from pathlib import Path

DATA_PATH = Path("data/raw/twcs.csv")

df = pd.read_csv(DATA_PATH)

print("=" * 60)
print("BRAND ANALYSIS")
print("=" * 60)

# Company accounts are represented by outbound tweets.
company_authors = df.loc[df["inbound"] == False, "author_id"]

brand_counts = company_authors.value_counts()

print("\nTop 30 company accounts:")
print(brand_counts.head(30))