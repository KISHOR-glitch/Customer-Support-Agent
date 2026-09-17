import json
import random
from pathlib import Path

INPUT_PATH = Path(
    "data/processed/apple_clean_cases.jsonl"
)

OUTPUT_PATH = Path(
    "data/golden/golden_set.jsonl"
)

SAMPLE_SIZE = 200
RANDOM_SEED = 42


# ============================================================
# LOAD CLEAN CASES
# ============================================================

print("Loading clean cases...")

cases = []

with open(
    INPUT_PATH,
    "r",
    encoding="utf-8"
) as f:

    for line in f:
        cases.append(json.loads(line))

print(f"Cases loaded: {len(cases):,}")


# ============================================================
# EXTRACT FIRST CUSTOMER MESSAGE
# ============================================================

examples = []

for case in cases:

    customer_messages = [
        message
        for message in case["messages"]
        if message["speaker"] == "customer"
    ]

    if not customer_messages:
        continue

    # First customer message
    message = customer_messages[0]

    text = message["text"].strip()

    if len(text) < 10:
        continue

    examples.append({
        "conversation_id": case["conversation_id"],
        "tweet_id": message["tweet_id"],
        "text": text
    })


print(
    f"Usable customer examples: "
    f"{len(examples):,}"
)


# ============================================================
# RANDOM SAMPLE
# ============================================================

random.seed(RANDOM_SEED)

sample_size = min(
    SAMPLE_SIZE,
    len(examples)
)

selected = random.sample(
    examples,
    sample_size
)


# ============================================================
# CREATE GOLDEN SET
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

    for example in selected:

        record = {
            "conversation_id":
                example["conversation_id"],

            "tweet_id":
                example["tweet_id"],

            "text":
                example["text"],

            # Human annotation
            "gold_intent": None,

            # We will use these later
            "gold_reply_quality": None,
            "gold_escalation": None,

            "notes": ""
        }

        f.write(
            json.dumps(
                record,
                ensure_ascii=False
            ) + "\n"
        )


# ============================================================
# DONE
# ============================================================

print()
print("=" * 60)
print("GOLDEN SET CREATED")
print("=" * 60)

print(f"Examples: {sample_size}")

print()
print("Output:")
print(OUTPUT_PATH)

print()
print("Next step:")
print("Manually label the gold_intent field.")