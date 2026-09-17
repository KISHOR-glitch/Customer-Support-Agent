import json
from pathlib import Path
from collections import Counter

INPUT_PATH = Path("data/golden/human_eval_outputs.jsonl")


def main():
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        data = [json.loads(line) for line in f]

    total = len(data)

    print("=" * 60)
    print("SUPPORTLENS AGENT EVALUATION")
    print("=" * 60)

    print(f"\nTotal evaluated cases: {total}")

    # Intent
    intent_correct = sum(
        x["gold_intent"] == x["predicted_intent"]
        for x in data
    )

    intent_accuracy = intent_correct / total if total else 0

    print("\nINTENT")
    print("-" * 60)
    print(f"Correct   : {intent_correct}/{total}")
    print(f"Accuracy  : {intent_accuracy:.4f}")

    # Escalation
    escalation_correct = sum(
        x["gold_escalation"] == x["predicted_escalation"]
        for x in data
    )

    escalation_accuracy = escalation_correct / total if total else 0

    print("\nESCALATION")
    print("-" * 60)
    print(f"Correct   : {escalation_correct}/{total}")
    print(f"Accuracy  : {escalation_accuracy:.4f}")

    # Confusion matrix
    print("\nESCALATION CONFUSION")
    print("-" * 60)

    confusion = Counter(
        (x["gold_escalation"], x["predicted_escalation"])
        for x in data
    )

    for key, value in confusion.items():
        print(f"{key}: {value}")

    # Human reply quality
    reply_distribution = Counter(
        x["gold_reply_quality"]
        for x in data
    )

    print("\nHUMAN REPLY QUALITY")
    print("-" * 60)

    for label, count in reply_distribution.items():
        print(f"{label}: {count}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()