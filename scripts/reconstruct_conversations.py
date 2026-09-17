import pandas as pd
import json
from pathlib import Path

# ============================================================
# CONFIG
# ============================================================

DATA_PATH = Path("data/raw/twcs.csv")
OUTPUT_PATH = Path("data/processed/apple_support_threads.jsonl")

BRAND = "AppleSupport"

# ============================================================
# LOAD DATA
# ============================================================

print("Loading dataset...")

df = pd.read_csv(DATA_PATH)

print(f"Total tweets: {len(df):,}")

# ============================================================
# CLEAN IDS
# ============================================================

df["tweet_id"] = pd.to_numeric(
    df["tweet_id"],
    errors="coerce"
)

df["in_response_to_tweet_id"] = pd.to_numeric(
    df["in_response_to_tweet_id"],
    errors="coerce"
)

df = df.dropna(subset=["tweet_id"])

df["tweet_id"] = df["tweet_id"].astype("int64")

# ============================================================
# LOOKUP
# ============================================================

tweets = df.set_index("tweet_id").to_dict("index")

# ============================================================
# APPLESUPPORT TWEETS
# ============================================================

apple = df[df["author_id"] == BRAND].copy()

print(f"AppleSupport tweets: {len(apple):,}")


# ============================================================
# GET SPEAKER
# ============================================================

def get_speaker(tweet):

    if tweet["author_id"] == BRAND:
        return "AppleSupport"

    return "customer"


# ============================================================
# BUILD SUPPORT THREAD
# ============================================================

def build_support_thread(start_id):

    thread = []

    current_id = start_id

    visited = set()

    while current_id in tweets:

        # Prevent loops
        if current_id in visited:
            break

        visited.add(current_id)

        current = tweets[current_id]

        current_speaker = get_speaker(current)

        # Add current tweet
        thread.append({
            "tweet_id": int(current_id),
            "speaker": current_speaker,
            "text": str(current["text"]),
            "created_at": str(current["created_at"])
        })

        # Find parent
        parent_id = current["in_response_to_tweet_id"]

        if pd.isna(parent_id):
            break

        parent_id = int(parent_id)

        if parent_id not in tweets:
            break

        parent = tweets[parent_id]

        parent_speaker = get_speaker(parent)

        # ====================================================
        # ONLY ALLOW CUSTOMER <-> APPLESUPPORT
        # ====================================================

        if current_speaker == "AppleSupport":

            # AppleSupport should reply to customer
            if parent_speaker != "customer":
                break

        elif current_speaker == "customer":

            # Customer should reply to AppleSupport
            if parent_speaker != "AppleSupport":
                break

        current_id = parent_id

    # We walked backwards
    thread.reverse()

    return thread


# ============================================================
# RECONSTRUCT
# ============================================================

threads = []

seen_brand_tweets = set()

print("Reconstructing support threads...")

for _, row in apple.iterrows():

    brand_tweet_id = int(row["tweet_id"])

    # Already included in another thread
    if brand_tweet_id in seen_brand_tweets:
        continue

    thread = build_support_thread(brand_tweet_id)

    if len(thread) < 2:
        continue

    speakers = [m["speaker"] for m in thread]

    # Must contain both
    if "customer" not in speakers:
        continue

    if "AppleSupport" not in speakers:
        continue

    # ========================================================
    # VERIFY ALTERNATING PATTERN
    # ========================================================

    valid = True

    for i in range(1, len(thread)):

        previous = thread[i - 1]["speaker"]
        current = thread[i]["speaker"]

        if previous == current:
            valid = False
            break

    if not valid:
        continue

    # ========================================================
    # MARK APPLESUPPORT TWEETS
    # ========================================================

    for message in thread:

        if message["speaker"] == "AppleSupport":
            seen_brand_tweets.add(
                message["tweet_id"]
            )

    # ========================================================
    # SAVE
    # ========================================================

    threads.append({
        "conversation_id": str(thread[0]["tweet_id"]),
        "message_count": len(thread),
        "messages": thread
    })


# ============================================================
# SAVE JSONL
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

    for thread in threads:

        f.write(
            json.dumps(
                thread,
                ensure_ascii=False
            ) + "\n"
        )


# ============================================================
# STATISTICS
# ============================================================

print()
print("=" * 60)
print("SUPPORT THREAD RECONSTRUCTION COMPLETE")
print("=" * 60)

print(
    f"AppleSupport tweets:       "
    f"{len(apple):,}"
)

print(
    f"Valid support threads:      "
    f"{len(threads):,}"
)

if threads:

    lengths = [
        t["message_count"]
        for t in threads
    ]

    two_message = sum(
        x == 2 for x in lengths
    )

    multi_turn = sum(
        x >= 4 for x in lengths
    )

    print(
        f"Average messages/thread:   "
        f"{sum(lengths) / len(lengths):.2f}"
    )

    print(
        f"Longest thread:            "
        f"{max(lengths)}"
    )

    print(
        f"2-message threads:         "
        f"{two_message:,}"
    )

    print(
        f"Multi-turn threads (4+):   "
        f"{multi_turn:,}"
    )

print()
print("Saved to:")
print(OUTPUT_PATH)


# ============================================================
# SHOW EXAMPLE
# ============================================================

if threads:

    # Prefer a multi-turn example
    multi_turn_threads = [
        t for t in threads
        if t["message_count"] >= 4
    ]

    if multi_turn_threads:

        example = multi_turn_threads[0]

    else:

        example = threads[0]

    print()
    print("=" * 60)
    print("EXAMPLE SUPPORT THREAD")
    print("=" * 60)

    for message in example["messages"]:

        print(
            f"\n[{message['speaker']}]"
        )

        print(message["text"])