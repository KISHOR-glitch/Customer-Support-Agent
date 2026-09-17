import pandas as pd
import json
from pathlib import Path

# ============================================================
# CONFIG
# ============================================================

DATA_PATH = Path("data/raw/twcs.csv")
OUTPUT_PATH = Path("data/processed/apple_conversations.jsonl")

BRAND = "AppleSupport"

# ============================================================
# 1. LOAD DATA
# ============================================================

print("Loading dataset...")

df = pd.read_csv(DATA_PATH)

print(f"Total tweets: {len(df):,}")

# ============================================================
# 2. CLEAN IMPORTANT COLUMNS
# ============================================================

df["tweet_id"] = pd.to_numeric(df["tweet_id"], errors="coerce")
df["in_response_to_tweet_id"] = pd.to_numeric(
    df["in_response_to_tweet_id"],
    errors="coerce"
)

# ============================================================
# 3. GET APPLESUPPORT REPLIES
# ============================================================

brand = df[df["author_id"] == BRAND].copy()

print(f"{BRAND} tweets: {len(brand):,}")

# ============================================================
# 4. KEEP ONLY REPLIES TO ANOTHER TWEET
# ============================================================

brand = brand.dropna(subset=["in_response_to_tweet_id"]).copy()

# Convert parent ID to integer
brand["in_response_to_tweet_id"] = (
    brand["in_response_to_tweet_id"].astype("int64")
)

# ============================================================
# 5. GET CUSTOMER TWEETS
# ============================================================

# We only need inbound tweets because those are customer messages.
customers = df[df["inbound"] == True].copy()

customers = customers[
    [
        "tweet_id",
        "author_id",
        "text",
        "created_at",
        "inbound"
    ]
].copy()

# ============================================================
# 6. MATCH APPLESUPPORT REPLIES TO CUSTOMER TWEETS
# ============================================================

conversations = brand.merge(
    customers,
    left_on="in_response_to_tweet_id",
    right_on="tweet_id",
    how="inner",
    suffixes=("_brand", "_customer")
)

print(
    f"Customer → {BRAND} pairs: "
    f"{len(conversations):,}"
)

# ============================================================
# 7. CREATE CLEAN OUTPUT
# ============================================================

output = conversations[
    [
        "tweet_id_customer",
        "tweet_id_brand",
        "text_customer",
        "text_brand",
        "created_at_customer",
        "created_at_brand"
    ]
].copy()

output.columns = [
    "customer_tweet_id",
    "brand_tweet_id",
    "customer_message",
    "brand_response",
    "customer_created_at",
    "brand_created_at"
]

# ============================================================
# 8. SAVE AS JSONL
# ============================================================

OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

with open(
    OUTPUT_PATH,
    "w",
    encoding="utf-8"
) as f:

    for record in output.to_dict(orient="records"):

        f.write(
            json.dumps(
                record,
                ensure_ascii=False
            ) + "\n"
        )

# ============================================================
# 9. SUMMARY
# ============================================================

print()
print("=" * 60)
print("DONE")
print("=" * 60)

print(f"{BRAND} tweets:        {len(brand):,}")
print(f"Customer pairs:     {len(output):,}")
print(f"Output file:        {OUTPUT_PATH}")

print()
print("Example:")
print(json.dumps(
    output.iloc[0].to_dict(),
    indent=2,
    ensure_ascii=False
))