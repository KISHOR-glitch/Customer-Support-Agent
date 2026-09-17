import json
import time
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.intents.classifier import predict_intent
from src.retrieval.bm25 import BM25Retriever
from src.generation.reply import generate_reply
from src.escalation.decision import decide_escalation


GOLDEN_PATH = Path("data/golden/golden_set.jsonl")
OUTPUT_PATH = Path("data/golden/human_eval_outputs.jsonl")
CASES_PATH = "data/processed/apple_clean_cases.jsonl"


def save_results(results):
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        for result in results:
            f.write(
                json.dumps(result, ensure_ascii=False) + "\n"
            )


def load_existing_results():
    if not OUTPUT_PATH.exists():
        return []

    with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def main():

    with open(GOLDEN_PATH, "r", encoding="utf-8") as f:
        all_cases = [json.loads(line) for line in f]

    # Only the 50 human-evaluated cases
    cases = [
        case for case in all_cases
        if case.get("gold_reply_quality") is not None
        and case.get("gold_escalation") is not None
    ]

    print(f"Total evaluation cases: {len(cases)}")

    # Load previously completed cases
    results = load_existing_results()

    completed_ids = {
        result["tweet_id"]
        for result in results
    }

    print(f"Already completed: {len(completed_ids)}")

    retriever = BM25Retriever(CASES_PATH)

    for i, case in enumerate(cases, 1):

        tweet_id = case["tweet_id"]

        # Skip completed cases
        if tweet_id in completed_ids:
            continue

        customer_message = case["text"]

        print("\n" + "=" * 70)
        print(f"Processing case {i}/{len(cases)}")
        print("=" * 70)
        print(customer_message)

        # Intent
        predicted_intent, intent_confidence = predict_intent(
            customer_message
        )

        # Retrieval
        retrieved_cases = retriever.search(
            customer_message,
            top_k=3
        )

        # Gemini reply with retries
        reply = None

        for attempt in range(3):

            try:
                reply = generate_reply(
                    customer_message,
                    retrieved_cases
                )
                break

            except Exception as e:
                print(
                    f"Gemini error (attempt {attempt + 1}/3): {e}"
                )

                if attempt < 2:
                    print("Waiting 5 seconds before retry...")
                    time.sleep(5)

        # If Gemini still fails, skip this case
        if reply is None:
            print("Skipping this case. Gemini unavailable.")
            continue

        # Escalation
        escalation = decide_escalation(
            customer_message,
            predicted_intent,
            retrieved_cases
        )

        result = {
            "conversation_id": case["conversation_id"],
            "tweet_id": tweet_id,
            "customer_message": customer_message,

            "gold_intent": case["gold_intent"],
            "predicted_intent": predicted_intent,
            "intent_confidence": intent_confidence,

            "reply": reply,

            "gold_reply_quality": case["gold_reply_quality"],
            "gold_escalation": case["gold_escalation"],

            "predicted_escalation": escalation["decision"],
            "escalation_reason": escalation["reason"],

            "retrieved_cases": [
                {
                    "conversation_id": r["conversation_id"],
                    "customer_text": r["customer_text"],
                    "support_messages": r["support_messages"],
                    "score": r["score"]
                }
                for r in retrieved_cases
            ]
        }

        results.append(result)

        # Save immediately
        save_results(results)

        print("Saved successfully.")

    print("\n" + "=" * 70)
    print("HUMAN EVALUATION OUTPUTS")
    print("=" * 70)
    print(f"Completed: {len(results)}/{len(cases)}")
    print(f"Output: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()