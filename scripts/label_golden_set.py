import json
import random
from pathlib import Path

GOLDEN_PATH = Path("data/golden/golden_set.jsonl")

SAMPLE_SIZE = 50
SEED = 42


def show_case(case, index):
    print("\n" + "=" * 70)
    print(f"CASE {index} / {SAMPLE_SIZE}")
    print("=" * 70)

    print("\nCustomer:")
    print(case["text"])

    print("\nCurrent intent:")
    print(case["gold_intent"])

    print("\nReply Quality:")
    print("1 = Good")
    print("2 = Acceptable")
    print("3 = Bad")

    while True:
        reply_quality = input("Choose reply quality (1/2/3): ").strip()

        if reply_quality in {"1", "2", "3"}:
            break

        print("Please enter 1, 2, or 3.")

    print("\nEscalation:")
    print("1 = AUTO-HANDLE")
    print("2 = ESCALATE")

    while True:
        escalation = input("Choose escalation (1/2): ").strip()

        if escalation in {"1", "2"}:
            break

        print("Please enter 1 or 2.")

    case["gold_reply_quality"] = {
        "1": "good",
        "2": "acceptable",
        "3": "bad"
    }[reply_quality]

    case["gold_escalation"] = {
        "1": "AUTO-HANDLE",
        "2": "ESCALATE"
    }[escalation]

    return case


def main():

    with open(GOLDEN_PATH, "r", encoding="utf-8") as f:
        cases = [json.loads(line) for line in f]

    print(f"Loaded {len(cases)} golden examples.")

    # Select exactly 50 cases
    random.seed(SEED)

    unlabeled = [
        case for case in cases
        if case.get("gold_reply_quality") is None
        and case.get("gold_escalation") is None
    ]

    sample_size = min(SAMPLE_SIZE, len(unlabeled))

    selected = random.sample(unlabeled, sample_size)

    print(f"Selected {sample_size} cases for human evaluation.")

    for i, case in enumerate(selected, 1):

        show_case(case, i)

        # Save immediately after every case
        with open(GOLDEN_PATH, "w", encoding="utf-8") as f:
            for item in cases:
                f.write(
                    json.dumps(
                        item,
                        ensure_ascii=False
                    ) + "\n"
                )

        print("\nSaved.")

    print("\n" + "=" * 70)
    print("50-CASE HUMAN EVALUATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()