import json
import random
import re
from pathlib import Path
from collections import Counter

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans


INPUT_PATH = Path(
    "data/processed/apple_clean_cases.jsonl"
)

OUTPUT_PATH = Path(
    "data/processed/intent_discovery.txt"
)

RANDOM_SEED = 42
SAMPLE_SIZE = 500
N_CLUSTERS = 12


# ============================================================
# LOAD CASES
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
# EXTRACT CUSTOMER MESSAGES
# ============================================================

customer_messages = []

for case in cases:

    for message in case["messages"]:

        if message["speaker"] == "customer":

            text = message["text"].strip()

            if len(text) >= 10:
                customer_messages.append(text)


print(
    f"Customer messages: "
    f"{len(customer_messages):,}"
)


# ============================================================
# RANDOM SAMPLE
# ============================================================

random.seed(RANDOM_SEED)

sample_size = min(
    SAMPLE_SIZE,
    len(customer_messages)
)

sample = random.sample(
    customer_messages,
    sample_size
)


# ============================================================
# TF-IDF
# ============================================================

print("Finding important terms...")

vectorizer = TfidfVectorizer(
    stop_words="english",
    max_features=3000,
    ngram_range=(1, 2),
    min_df=3
)

X = vectorizer.fit_transform(
    sample
)

terms = vectorizer.get_feature_names_out()


# ============================================================
# CLUSTER CUSTOMER MESSAGES
# ============================================================

print(
    f"Clustering into "
    f"{N_CLUSTERS} groups..."
)

kmeans = KMeans(
    n_clusters=N_CLUSTERS,
    random_state=RANDOM_SEED,
    n_init=10
)

labels = kmeans.fit_predict(X)


# ============================================================
# GET TOP TERMS PER CLUSTER
# ============================================================

cluster_terms = {}

for cluster_id in range(N_CLUSTERS):

    center = kmeans.cluster_centers_[cluster_id]

    top_indices = center.argsort()[-15:][::-1]

    cluster_terms[cluster_id] = [
        terms[i]
        for i in top_indices
    ]


# ============================================================
# BUILD OUTPUT
# ============================================================

output = []

output.append("=" * 70)
output.append("SUPPORTLENS — INTENT DISCOVERY")
output.append("=" * 70)

output.append(
    f"\nTotal clean cases: {len(cases):,}"
)

output.append(
    f"Customer messages: {len(customer_messages):,}"
)

output.append(
    f"Sample used: {sample_size:,}"
)

output.append(
    f"Clusters: {N_CLUSTERS}"
)

# ============================================================
# CLUSTER RESULTS
# ============================================================

for cluster_id in range(N_CLUSTERS):

    output.append("\n")
    output.append("=" * 70)

    cluster_messages = [
        sample[i]
        for i in range(len(sample))
        if labels[i] == cluster_id
    ]

    output.append(
        f"CLUSTER {cluster_id + 1}"
    )

    output.append(
        f"Messages: {len(cluster_messages)}"
    )

    output.append(
        "\nTop terms:"
    )

    output.append(
        ", ".join(
            cluster_terms[cluster_id]
        )
    )

    output.append(
        "\nExample messages:"
    )

    # Show up to 8 examples
    for message in cluster_messages[:8]:

        output.append(
            f"- {message}"
        )


# ============================================================
# RANDOM CUSTOMER SAMPLE
# ============================================================

output.append("\n")
output.append("=" * 70)
output.append("RANDOM CUSTOMER SAMPLE")
output.append("=" * 70)

for i, message in enumerate(sample[:100], 1):

    output.append(
        f"{i}. {message}"
    )


# ============================================================
# SAVE
# ============================================================

with open(
    OUTPUT_PATH,
    "w",
    encoding="utf-8"
) as f:

    f.write(
        "\n".join(output)
    )


print()
print("=" * 60)
print("INTENT DISCOVERY COMPLETE")
print("=" * 60)

print(
    f"Output: {OUTPUT_PATH}"
)

print()
print(
    "Open the output file and inspect the "
    "12 clusters."
)