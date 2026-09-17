import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import json

from src.escalation.decision import decide_escalation


INPUT_PATH = Path("data/golden/human_eval_outputs.jsonl")


def main():
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        cases = [json.loads(line) for line in f]

    errors = []

    for case in cases:
        decision, reason = decide_escalation(
            customer_message=case["customer_message"],
            predicted_intent=case["predicted_intent"],
            retrieved_cases=case.get("retrieved_cases", []),
        )

        if (
            case["gold_escalation"] == "ESCALATE"
            and decision == "AUTO-HANDLE"
        ):
            errors.append(
                {
                    "message": case["customer_message"],
                    "intent": case["predicted_intent"],
                    "gold": case["gold_escalation"],
                    "predicted": decision,
                    "reason": reason,
                }
            )

    print("=" * 70)
    print(f"FALSE AUTO-HANDLES: {len(errors)}")
    print("=" * 70)

    for i, error in enumerate(errors, 1):
        print(f"\n{i}. {error['message']}")
        print(f"   Intent    : {error['intent']}")
        print(f"   Gold      : {error['gold']}")
        print(f"   Predicted : {error['predicted']}")
        print(f"   Reason    : {error['reason']}")


if __name__ == "__main__":
    main()