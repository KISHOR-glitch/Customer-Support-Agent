import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import json

from sklearn.metrics import accuracy_score, f1_score, classification_report

from src.intents.semantic_classifier import SemanticClassifier


GOLDEN_PATH = Path("data/golden/golden_set.jsonl")


def load_golden_set():
    examples = []

    with open(GOLDEN_PATH, "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)

            if item.get("gold_intent"):
                examples.append(item)

    return examples


def main():

    data = load_golden_set()

    print(f"Total labeled examples: {len(data)}")

    # Same split used by evaluate.py
    split = int(len(data) * 0.8)

    train_data = data[:split]
    test_data = data[split:]

    train_texts = [x["text"] for x in train_data]
    train_labels = [x["gold_intent"] for x in train_data]

    test_texts = [x["text"] for x in test_data]
    test_labels = [x["gold_intent"] for x in test_data]

    print(f"Training examples: {len(train_data)}")
    print(f"Test examples: {len(test_data)}")

    # Create and train classifier
    classifier = SemanticClassifier()

    classifier.train(
        train_texts,
        train_labels
    )

    # Predict test examples
    predictions = []

    for text in test_texts:
        prediction, confidence = classifier.predict(text)
        predictions.append(prediction)

    # Metrics
    accuracy = accuracy_score(
        test_labels,
        predictions
    )

    macro_f1 = f1_score(
        test_labels,
        predictions,
        average="macro",
        zero_division=0
    )

    print("\n" + "=" * 60)
    print("Final Semantic Classifier")
    print("=" * 60)

    print(f"Accuracy : {accuracy:.4f}")
    print(f"Macro F1 : {macro_f1:.4f}")

    print("\nPer-intent results:")

    print(
        classification_report(
            test_labels,
            predictions,
            zero_division=0
        )
    )


if __name__ == "__main__":
    main()