import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.intents.classifier import predict_intent
from src.retrieval.bm25 import BM25Retriever
from src.generation.reply import generate_reply
from src.escalation.decision import decide_escalation


CASES_PATH = "data/processed/apple_clean_cases.jsonl"


def main():
    retriever = BM25Retriever(CASES_PATH)

    customer_message = input("\nEnter customer message: ")

    # 1. Intent classification
    intent, intent_confidence = predict_intent(customer_message)

    # 2. Historical case retrieval
    retrieved_cases = retriever.search(
        customer_message,
        top_k=3
    )

    # 3. Generate grounded reply
    reply = generate_reply(
        customer_message,
        retrieved_cases
    )

    # 4. Escalation decision
    escalation = decide_escalation(
        customer_message,
        intent,
        retrieved_cases
    )

    # Final output
    print("\n" + "=" * 60)
    print("SUPPORTLENS RESULT")
    print("=" * 60)

    print("\nCUSTOMER MESSAGE")
    print("-" * 60)
    print(customer_message)

    print("\nINTENT")
    print("-" * 60)
    print(f"Intent     : {intent}")
    print(f"Confidence : {intent_confidence:.2f}")

    print("\nRETRIEVAL")
    print("-" * 60)

    if retrieved_cases:
        print(f"Cases retrieved : {len(retrieved_cases)}")
        print(f"Top BM25 score  : {retrieved_cases[0]['score']:.2f}")

        print("\nTop evidence:")
        print(f"Customer: {retrieved_cases[0]['customer_text']}")

        for message in retrieved_cases[0]["support_messages"]:
            print(f"AppleSupport: {message['text']}")
    else:
        print("No historical cases found.")

    print("\nDRAFT REPLY")
    print("-" * 60)
    print(reply)

    print("\nESCALATION")
    print("-" * 60)
    print(f"Decision : {escalation['decision']}")
    print(f"Reason   : {escalation['reason']}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()