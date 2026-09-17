import json
import re
from pathlib import Path

INPUT_PATH = Path(
    "data/processed/apple_support_threads.jsonl"
)

OUTPUT_PATH = Path(
    "data/processed/apple_clean_cases.jsonl"
)

# ============================================================
# CLOSING / LOW-VALUE MESSAGES
# ============================================================

CLOSING_MESSAGES = {
    "thank you",
    "thanks",
    "thank u",
    "thx",
    "ty",
    "you're welcome",
    "you are welcome",
    "thanks apple",
    "thank you apple",
    "great thanks",
    "ok thanks",
    "okay thanks",
}


# ============================================================
# CLEAN TEXT
# ============================================================

def clean_text(text):

    text = str(text)

    # Remove URLs
    text = re.sub(
        r"https?://\S+",
        "",
        text
    )

    # Remove @mentions
    text = re.sub(
        r"@\w+",
        "",
        text
    )

    # Remove HTML entities
    text = re.sub(
        r"&gt;",
        ">",
        text
    )

    text = re.sub(
        r"&lt;",
        "<",
        text
    )

    # Normalize whitespace
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# LOW-VALUE MESSAGE
# ============================================================

def is_low_value(text):

    text = clean_text(text).lower().strip()

    if not text:
        return True

    if text in CLOSING_MESSAGES:
        return True

    # Very short message
    if len(text) <= 3:
        return True

    return False


# ============================================================
# CHECK WHETHER CUSTOMER HAS A REAL SUPPORT REQUEST
# ============================================================

def contains_support_signal(text):

    text = clean_text(text).lower()

    # Exact phrases / words
    support_phrases = [
        "help",
        "problem",
        "issue",
        "error",
        "can't",
        "cannot",
        "won't",
        "not working",
        "doesn't work",
        "unable",
        "broken",
        "why",
        "how do",
        "how can",
        "stuck",
        "failed",
        "failure",
        "crash",
        "crashing",
        "update",
        "login",
        "log in",
        "password",
        "account",
        "battery",
        "iphone",
        "ipad",
        "icloud",
        "itunes",
    ]

    # Word-boundary matching.
    # Prevents things like "AppleSupport" matching "app".
    for phrase in support_phrases:

        pattern = r"\b" + re.escape(phrase) + r"\b"

        if re.search(pattern, text):
            return True

    # Question
    if "?" in text:
        return True

    # Substantial message
    if len(text) >= 50:
        return True

    return False


# ============================================================
# LOAD
# ============================================================

print("Loading reconstructed conversations...")

threads = []

with open(
    INPUT_PATH,
    "r",
    encoding="utf-8"
) as f:

    for line in f:

        threads.append(
            json.loads(line)
        )

print(
    f"Input threads: {len(threads):,}"
)


# ============================================================
# CLEAN
# ============================================================

clean_cases = []

removed_short = 0
removed_low_value = 0
removed_no_problem = 0


for thread in threads:

    messages = thread["messages"]

    cleaned_messages = []

    # --------------------------------------------------------
    # Clean every message
    # --------------------------------------------------------

    for message in messages:

        text = clean_text(
            message["text"]
        )

        if not text:
            continue

        cleaned_messages.append({
            "tweet_id": message["tweet_id"],
            "speaker": message["speaker"],
            "text": text,
            "created_at": message["created_at"]
        })

    # --------------------------------------------------------
    # Must contain at least 2 messages
    # --------------------------------------------------------

    if len(cleaned_messages) < 2:

        removed_short += 1
        continue

    # --------------------------------------------------------
    # Separate speakers
    # --------------------------------------------------------

    customer_messages = [
        m for m in cleaned_messages
        if m["speaker"] == "customer"
    ]

    brand_messages = [
        m for m in cleaned_messages
        if m["speaker"] == "AppleSupport"
    ]

    if not customer_messages or not brand_messages:

        removed_short += 1
        continue

    # --------------------------------------------------------
    # Remove low-value customer messages
    # ONLY for deciding whether conversation is useful.
    # We keep the actual messages.
    # --------------------------------------------------------

    useful_customer_messages = [
        m for m in customer_messages
        if not is_low_value(m["text"])
    ]

    if not useful_customer_messages:

        removed_low_value += 1
        continue

    # --------------------------------------------------------
    # Find actual support signal
    # --------------------------------------------------------

    has_problem = any(
        contains_support_signal(
            m["text"]
        )
        for m in useful_customer_messages
    )

    if not has_problem:

        removed_no_problem += 1
        continue

    # --------------------------------------------------------
    # Keep case
    # --------------------------------------------------------

    clean_cases.append({

        "conversation_id":
            thread["conversation_id"],

        "message_count":
            len(cleaned_messages),

        "messages":
            cleaned_messages
    })


# ============================================================
# SAVE
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

    for case in clean_cases:

        f.write(
            json.dumps(
                case,
                ensure_ascii=False
            ) + "\n"
        )


# ============================================================
# STATISTICS
# ============================================================

print()
print("=" * 60)
print("CLEANING COMPLETE")
print("=" * 60)

print(
    f"Input threads:             "
    f"{len(threads):,}"
)

print(
    f"Clean support cases:       "
    f"{len(clean_cases):,}"
)

print()

print(
    f"Removed short:             "
    f"{removed_short:,}"
)

print(
    f"Removed low-value:         "
    f"{removed_low_value:,}"
)

print(
    f"Removed no problem:        "
    f"{removed_no_problem:,}"
)

if clean_cases:

    lengths = [
        c["message_count"]
        for c in clean_cases
    ]

    print()

    print(
        f"Average messages/case:     "
        f"{sum(lengths) / len(lengths):.2f}"
    )

    print(
        f"Longest case:              "
        f"{max(lengths)}"
    )

print()
print("Output:")
print(OUTPUT_PATH)


# ============================================================
# SHOW EXAMPLES
# ============================================================

print()
print("=" * 60)
print("EXAMPLE CLEAN CASES")
print("=" * 60)

for case in clean_cases[:5]:

    print()
    print("-" * 60)

    for message in case["messages"]:

        print(
            f"[{message['speaker']}] "
            f"{message['text']}"
        )