import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import json

from sklearn.metrics import accuracy_score, f1_score, classification_report

from src.intents.classifier import predict_intent
from src.intents.baselines import get_majority_intent, predict_majority


# --------------------------------------------------
# Paths
# --------------------------------------------------

GOLDEN_PATH = Path("data/golden/golden_set.jsonl")


# --------------------------------------------------
# Load golden set
# --------------------------------------------------

def load_golden_set():
    examples = []

    with open(GOLDEN_PATH, "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)

            if item.get("gold_intent"):
                examples.append(item)

    return examples


# --------------------------------------------------
# Evaluation
# --------------------------------------------------

def evaluate(name, y_true, y_pred):

    accuracy = accuracy_score(y_true, y_pred)

    macro_f1 = f1_score(
        y_true,
        y_pred,
        average="macro",
        zero_division=0
    )

    print("\n" + "=" * 60)
    print(name)
    print("=" * 60)

    print(f"Accuracy : {accuracy:.4f}")
    print(f"Macro F1 : {macro_f1:.4f}")

    print("\nPer-intent results:")
    print(
        classification_report(
            y_true,
            y_pred,
            zero_division=0
        )
    )


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    data = load_golden_set()

    print(f"Golden examples: {len(data)}")

    # Reproducible split
    # 80% = development
    # 20% = held-out test
    split = int(len(data) * 0.8)

    dev = data[:split]
    test = data[split:]

    y_dev = [x["gold_intent"] for x in dev]
    y_true = [x["gold_intent"] for x in test]

    texts = [x["text"] for x in test]

    print(f"Development examples: {len(dev)}")
    print(f"Test examples: {len(test)}")

    # --------------------------------------------------
    # Baseline 1: Majority Class
    # --------------------------------------------------

    majority_intent = get_majority_intent(y_dev)

    print(f"\nMajority intent: {majority_intent}")

    majority_predictions = [
        predict_majority(text, majority_intent)
        for text in texts
    ]

    evaluate(
        "Baseline 1 - Majority Class",
        y_true,
        majority_predictions
    )

    # --------------------------------------------------
    # Baseline 2: Keyword / Rule Classifier
    # --------------------------------------------------

    keyword_predictions = [
        predict_intent(text)[0]
        for text in texts
    ]

    evaluate(
        "Baseline 2 - Keyword / Rule Classifier",
        y_true,
        keyword_predictions
    )


if __name__ == "__main__":
    main()