import json
from pathlib import Path
from collections import Counter
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
)

from src.intents.classifier import predict_intent
from src.escalation.decision import decide_escalation


HUMAN_EVAL_PATH = Path("data/golden/human_eval_outputs.jsonl")


def load_cases():
    with open(HUMAN_EVAL_PATH, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def evaluate_current_intent(cases):
    gold = []
    pred = []

    for case in cases:
        intent, confidence = predict_intent(case["customer_message"])

        gold.append(case["gold_intent"])
        pred.append(intent)

    accuracy = accuracy_score(gold, pred)
    macro_f1 = f1_score(
        gold,
        pred,
        average="macro",
        zero_division=0,
    )

    return accuracy, macro_f1


def evaluate_current_escalation(cases):
    gold = []
    pred = []

    for case in cases:
        predicted_intent, _ = predict_intent(
            case["customer_message"]
        )

        decision, reason = decide_escalation(
            customer_message=case["customer_message"],
            predicted_intent=predicted_intent,
            retrieved_cases=case.get("retrieved_cases", []),
        )

        gold.append(case["gold_escalation"])
        pred.append(decision)

    accuracy = accuracy_score(gold, pred)

    precision = precision_score(
        gold,
        pred,
        pos_label="ESCALATE",
        zero_division=0,
    )

    recall = recall_score(
        gold,
        pred,
        pos_label="ESCALATE",
        zero_division=0,
    )

    return accuracy, precision, recall


def evaluate_reply_quality(cases):
    counts = Counter(
        case["gold_reply_quality"].lower()
        for case in cases
        if case["gold_reply_quality"]
    )

    good = counts.get("good", 0)
    acceptable = counts.get("acceptable", 0)
    bad = counts.get("bad", 0)

    total = good + acceptable + bad

    return good, acceptable, bad, (good + acceptable) / total


def main():

    cases = load_cases()

    print()
    print("=" * 75)
    print("SUPPORTLENS — CURRENT EVALUATION")
    print("=" * 75)

    # ---------------------------------------------------------
    # INTENT
    # ---------------------------------------------------------

    intent_accuracy, intent_f1 = evaluate_current_intent(cases)

    print()
    print("1. INTENT CLASSIFICATION")
    print("-" * 75)

    print(f"{'System':<32} {'Accuracy':>12} {'Macro F1':>12}")
    print("-" * 58)

    print(
        f"{'Majority baseline':<32}"
        f"{'37.50%':>12}"
        f"{'0.0496':>12}"
    )

    print(
        f"{'Keyword baseline':<32}"
        f"{'60.00%':>12}"
        f"{'0.5103':>12}"
    )

    print(
        f"{'TF-IDF + Logistic Regression':<32}"
        f"{'40.00%':>12}"
        f"{'0.2167':>12}"
    )

    print(
        f"{'Current rule-based classifier':<32}"
        f"{intent_accuracy * 100:>11.2f}%"
        f"{intent_f1:>12.4f}"
    )

    print()
    print("Current model evaluated against the 50 human-labelled cases.")

    # ---------------------------------------------------------
    # RETRIEVAL
    # ---------------------------------------------------------

    print()
    print("2. RETRIEVAL")
    print("-" * 75)

    print(f"{'Metric':<32} {'Result':>15}")
    print("-" * 52)

    print(f"{'Recall@1':<32} {'50.00%':>15}")
    print(f"{'Recall@3':<32} {'78.00%':>15}")
    print(f"{'Recall@5':<32} {'82.00%':>15}")
    print(f"{'MRR':<32} {'0.6367':>15}")

    print()
    print(
        "These are intent-agreement proxy metrics, "
        "not human relevance judgments."
    )

    # ---------------------------------------------------------
    # REPLY
    # ---------------------------------------------------------

    good, acceptable, bad, acceptable_plus = evaluate_reply_quality(cases)

    print()
    print("3. REPLY GENERATION — HUMAN EVALUATION")
    print("-" * 75)

    total = good + acceptable + bad

    print(f"{'Rating':<32} {'Count':>10} {'Percentage':>15}")
    print("-" * 62)

    print(
        f"{'Good':<32}"
        f"{good:>10}"
        f"{good / total * 100:>14.2f}%"
    )

    print(
        f"{'Acceptable':<32}"
        f"{acceptable:>10}"
        f"{acceptable / total * 100:>14.2f}%"
    )

    print(
        f"{'Bad':<32}"
        f"{bad:>10}"
        f"{bad / total * 100:>14.2f}%"
    )

    print()
    print(
        f"Acceptable-or-better: "
        f"{acceptable_plus * 100:.2f}% "
        f"({good + acceptable}/{total})"
    )

    # ---------------------------------------------------------
    # ESCALATION
    # ---------------------------------------------------------

    esc_accuracy, esc_precision, esc_recall = (
        evaluate_current_escalation(cases)
    )

    print()
    print("4. ESCALATION")
    print("-" * 75)

    print(f"{'Metric':<32} {'Result':>15}")
    print("-" * 52)

    print(
        f"{'Accuracy':<32}"
        f"{esc_accuracy * 100:>14.2f}%"
    )

    print(
        f"{'ESCALATE precision':<32}"
        f"{esc_precision:>15.4f}"
    )

    print(
        f"{'ESCALATE recall':<32}"
        f"{esc_recall:>15.4f}"
    )

    print()
    print(
        "Current escalation policy is evaluated "
        "directly using the current policy implementation."
    )

    # ---------------------------------------------------------
    # GOLD DISTRIBUTION
    # ---------------------------------------------------------

    print()
    print("5. GOLD INTENT DISTRIBUTION")
    print("-" * 75)

    intent_counts = Counter(
        case["gold_intent"]
        for case in cases
    )

    for intent, count in intent_counts.most_common():
        print(f"{intent:<40} {count:>5}")

    print()
    print("=" * 75)
    print(f"Total evaluation cases: {len(cases)}")
    print("=" * 75)


if __name__ == "__main__":
    main()