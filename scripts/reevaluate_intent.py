import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import json
from collections import Counter
from src.intents.classifier import predict_intent


INPUT_PATH = Path("data/golden/human_eval_outputs.jsonl")


def main():
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        data = [json.loads(line) for line in f]

    correct = 0
    total = len(data)

    errors = []
    confusion = Counter()

    for case in data:
        predicted, confidence = predict_intent(
            case["customer_message"]
        )

        gold = case["gold_intent"]

        confusion[(gold, predicted)] += 1

        if predicted == gold:
            correct += 1
        else:
            errors.append(
                (case["customer_message"], gold, predicted)
            )

    accuracy = correct / total if total else 0

    print("=" * 60)
    print("RE-EVALUATED INTENT CLASSIFIER")
    print("=" * 60)

    print(f"\nTotal cases : {total}")
    print(f"Correct     : {correct}/{total}")
    print(f"Accuracy    : {accuracy:.4f}")

    print("\nINTENT ERRORS")
    print("-" * 60)

    for i, (message, gold, predicted) in enumerate(errors, 1):
        print(f"\n{i}. {message}")
        print(f"   Gold      : {gold}")
        print(f"   Predicted : {predicted}")

    print("\nCONFUSION SUMMARY")
    print("-" * 60)

    for (gold, predicted), count in confusion.items():
        if gold != predicted:
            print(f"{gold} -> {predicted}: {count}")


if __name__ == "__main__":
    main()