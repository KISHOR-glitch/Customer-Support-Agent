import pandas as pd
from pathlib import Path

DATA_PATH = Path("data/raw/twcs.csv")

BRAND = "AppleSupport"

df = pd.read_csv(DATA_PATH)

brand = df[df["author_id"] == BRAND].copy()

print("=" * 60)
print(f"ANALYSIS: {BRAND}")
print("=" * 60)

print(f"\nTotal brand tweets: {len(brand):,}")

print("\nInbound / outbound:")
print(brand["inbound"].value_counts())

print(f"\nUnique conversations referenced:")
print(brand["in_response_to_tweet_id"].nunique())

print("\nDate range:")
print("Start:", brand["created_at"].min())
print("End:  ", brand["created_at"].max())

print("\nSample AppleSupport replies:")
print()

for _, row in brand.head(20).iterrows():
    print("-" * 60)
    print(row["text"])