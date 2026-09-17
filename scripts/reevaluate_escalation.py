import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import json
from collections import Counter

from src.escalation.decision import decide_escalation


INPUT_PATH = Path("data/golden/human_eval_outputs.jsonl")


def main():
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        cases = [json.loads(line) for line in f]

    correct = 0
    confusion = Counter()

    for case in cases:
        decision, reason = decide_escalation(
            customer_message=case["customer_message"],
            predicted_intent=case["predicted_intent"],
            retrieved_cases=case.get("retrieved_cases", []),
        )

        gold = case["gold_escalation"]

        confusion[(gold, decision)] += 1

        if gold == decision:
            correct += 1

    total = len(cases)
    accuracy = correct / total if total else 0

    print("=" * 60)
    print("RE-EVALUATED ESCALATION POLICY")
    print("=" * 60)

    print(f"\nTotal cases : {total}")
    print(f"Correct     : {correct}/{total}")
    print(f"Accuracy    : {accuracy:.4f}")

    print("\nCONFUSION MATRIX")
    print("-" * 60)

    for pair, count in confusion.items():
        print(f"{pair}: {count}")


if __name__ == "__main__":
    main()