import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.intents.classifier import predict_intent
from src.retrieval.bm25 import BM25Retriever
from src.escalation.decision import decide_escalation


CASES_PATH = "data/processed/apple_clean_cases.jsonl"


def main():

    retriever = BM25Retriever(CASES_PATH)

    print("SupportLens Escalation Test")
    print("Type 'exit' to stop.")
    print("-" * 60)

    while True:

        customer_message = input(
            "\nEnter customer message: "
        )

        if customer_message.lower() == "exit":
            break

        # ---------------------------------------------
        # 1. Predict intent
        # ---------------------------------------------

        intent, confidence = predict_intent(
            customer_message
        )

        # ---------------------------------------------
        # 2. Retrieve historical cases
        # ---------------------------------------------

        results = retriever.search(
            customer_message,
            top_k=3
        )

        # ---------------------------------------------
        # 3. Decide escalation
        # ---------------------------------------------

        decision = decide_escalation(
            customer_message,
            intent,
            results
        )

        # ---------------------------------------------
        # Output
        # ---------------------------------------------

        print("\n" + "=" * 60)

        print("INTENT")
        print("=" * 60)

        print(f"Intent     : {intent}")
        print(f"Confidence : {confidence}")

        print("\n" + "=" * 60)

        print("RETRIEVAL")
        print("=" * 60)

        if results:
            print(f"Top score  : {results[0]['score']:.2f}")
            print(f"Cases found: {len(results)}")
        else:
            print("No cases found.")

        print("\n" + "=" * 60)

        print("ESCALATION")
        print("=" * 60)

        print(f"Decision : {decision['decision']}")
        print(f"Reason   : {decision['reason']}")

        print("=" * 60)


if __name__ == "__main__":
    main()