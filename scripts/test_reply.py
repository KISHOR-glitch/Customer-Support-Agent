import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.retrieval.bm25 import BM25Retriever
from src.generation.reply import generate_reply


CASES_PATH = "data/processed/apple_clean_cases.jsonl"


def main():

    retriever = BM25Retriever(CASES_PATH)

    customer_message = input(
        "Enter customer message: "
    )

    # Retrieve top 3 similar historical cases
    results = retriever.search(
        customer_message,
        top_k=3
    )

    print("\n" + "=" * 60)
    print("RETRIEVED CASES")
    print("=" * 60)

    for i, result in enumerate(results, 1):

        print(f"\nCase {i}")
        print(f"Conversation ID: {result['conversation_id']}")
        print(f"Score: {result['score']:.2f}")
        print(f"Customer: {result['customer_text']}")

        for message in result["support_messages"]:
            print(
                f"AppleSupport: {message['text']}"
            )

    print("\n" + "=" * 60)
    print("GENERATING REPLY...")
    print("=" * 60)

    reply = generate_reply(
        customer_message,
        results
    )

    print("\n" + "=" * 60)
    print("DRAFT REPLY")
    print("=" * 60)

    print(reply)


if __name__ == "__main__":
    main()