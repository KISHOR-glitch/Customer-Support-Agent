import json
from pathlib import Path
from collections import Counter


INPUT_PATH = Path("data/golden/llm_judged_outputs.jsonl")


def normalize_quality(value):
    if not value:
        return None

    return value.strip().lower()


def main():

    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        cases = [json.loads(line) for line in f]

    total = len(cases)

    print("=" * 60)
    print("SUPPORTLENS LLM JUDGE EVALUATION")
    print("=" * 60)

    print(f"\nTotal judged cases: {total}")

    # ==================================================
    # HUMAN REPLY QUALITY
    # ==================================================

    human_quality = Counter(
        normalize_quality(case.get("gold_reply_quality"))
        for case in cases
        if case.get("gold_reply_quality")
    )

    print("\nHUMAN REPLY QUALITY")
    print("-" * 60)

    for label, count in human_quality.items():
        print(f"{label}: {count}")

    human_acceptable = (
        human_quality.get("good", 0)
        + human_quality.get("acceptable", 0)
    )

    print(
        f"\nHuman ≥ acceptable: "
        f"{human_acceptable}/{total} "
        f"= {human_acceptable / total:.2%}"
    )

    # ==================================================
    # LLM REPLY QUALITY
    # ==================================================

    llm_quality = Counter(
        normalize_quality(case.get("llm_reply_quality"))
        for case in cases
        if case.get("llm_reply_quality")
    )

    print("\nLLM REPLY QUALITY")
    print("-" * 60)

    for label, count in llm_quality.items():
        print(f"{label}: {count}")

    llm_acceptable = (
        llm_quality.get("good", 0)
        + llm_quality.get("acceptable", 0)
    )

    print(
        f"\nLLM ≥ acceptable: "
        f"{llm_acceptable}/{total} "
        f"= {llm_acceptable / total:.2%}"
    )

    # ==================================================
    # HUMAN vs LLM REPLY AGREEMENT
    # ==================================================

    quality_pairs = Counter()

    for case in cases:

        human = normalize_quality(
            case.get("gold_reply_quality")
        )

        llm = normalize_quality(
            case.get("llm_reply_quality")
        )

        if human and llm:
            quality_pairs[(human, llm)] += 1

    quality_agreement = sum(
        count
        for (human, llm), count in quality_pairs.items()
        if human == llm
    )

    quality_total = sum(quality_pairs.values())

    print("\nHUMAN vs LLM REPLY QUALITY")
    print("-" * 60)

    for pair, count in quality_pairs.items():
        print(f"{pair}: {count}")

    if quality_total:
        print(
            f"\nExact agreement: "
            f"{quality_agreement}/{quality_total} "
            f"= {quality_agreement / quality_total:.2%}"
        )

    # ==================================================
    # HUMAN vs LLM ESCALATION
    # ==================================================

    escalation_pairs = Counter()

    for case in cases:

        human = case.get("gold_escalation")
        llm = case.get("llm_escalation")

        if human and llm:
            escalation_pairs[(human, llm)] += 1

    escalation_agreement = sum(
        count
        for (human, llm), count in escalation_pairs.items()
        if human == llm
    )

    escalation_total = sum(escalation_pairs.values())

    print("\nHUMAN vs LLM ESCALATION")
    print("-" * 60)

    for pair, count in escalation_pairs.items():
        print(f"{pair}: {count}")

    if escalation_total:
        print(
            f"\nExact agreement: "
            f"{escalation_agreement}/{escalation_total} "
            f"= {escalation_agreement / escalation_total:.2%}"
        )

    # ==================================================
    # SUMMARY
    # ==================================================

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    print(
        f"\nHuman reply ≥ acceptable: "
        f"{human_acceptable}/{total} "
        f"= {human_acceptable / total:.2%}"
    )

    print(
        f"LLM reply ≥ acceptable: "
        f"{llm_acceptable}/{total} "
        f"= {llm_acceptable / total:.2%}"
    )

    if quality_total:
        print(
            f"Human-LLM reply agreement: "
            f"{quality_agreement}/{quality_total} "
            f"= {quality_agreement / quality_total:.2%}"
        )

    if escalation_total:
        print(
            f"Human-LLM escalation agreement: "
            f"{escalation_agreement}/{escalation_total} "
            f"= {escalation_agreement / escalation_total:.2%}"
        )


if __name__ == "__main__":
    main()