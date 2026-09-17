import json
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.retrieval.bm25 import BM25Retriever
from src.intents.classifier import predict_intent


INPUT_PATH = Path("data/golden/human_eval_outputs.jsonl")
CASES_PATH = Path("data/processed/apple_clean_cases.jsonl")


def main():
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        cases = [json.loads(line) for line in f]

    print("Loading BM25 index...")
    retriever = BM25Retriever(CASES_PATH)

    recall_1 = 0
    recall_3 = 0
    recall_5 = 0
    mrr_total = 0

    for case in cases:
        query = case["customer_message"]
        gold_intent = case["gold_intent"]
        current_id = str(case["conversation_id"])

        # Retrieve extra results so we can remove the query itself.
        results = retriever.search(query, top_k=10)

        # Remove the exact evaluation conversation.
        results = [
            r for r in results
            if str(r["conversation_id"]) != current_id
        ]

        # Keep top 5 after leakage removal.
        results = results[:5]

        retrieved_intents = []

        for result in results:
            intent, confidence = predict_intent(
                result["customer_text"]
            )
            retrieved_intents.append(intent)

        # Recall@1
        if gold_intent in retrieved_intents[:1]:
            recall_1 += 1

        # Recall@3
        if gold_intent in retrieved_intents[:3]:
            recall_3 += 1

        # Recall@5
        if gold_intent in retrieved_intents[:5]:
            recall_5 += 1

        # MRR
        reciprocal_rank = 0

        for rank, intent in enumerate(retrieved_intents, start=1):
            if intent == gold_intent:
                reciprocal_rank = 1 / rank
                break

        mrr_total += reciprocal_rank

    n = len(cases)

    print()
    print("=" * 70)
    print("LEAKAGE-SAFE BM25 RETRIEVAL EVALUATION")
    print("=" * 70)

    print(f"Cases evaluated: {n}")
    print()

    print("Intent-based Proxy Retrieval Metrics")
    print("-" * 45)

    print(f"Recall@1 : {recall_1 / n:.4f}")
    print(f"Recall@3 : {recall_3 / n:.4f}")
    print(f"Recall@5 : {recall_5 / n:.4f}")
    print(f"MRR      : {mrr_total / n:.4f}")

    print()
    print("NOTE:")
    print("These are proxy metrics based on intent agreement.")
    print("They are not manually judged retrieval relevance metrics.")


if __name__ == "__main__":
    main()