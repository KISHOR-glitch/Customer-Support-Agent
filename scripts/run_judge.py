import json
from pathlib import Path
import sys
import time
import argparse

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.evaluation.judge import judge_case


INPUT_PATH = Path(
    "data/golden/human_eval_outputs.jsonl"
)

OUTPUT_PATH = Path(
    "data/golden/llm_judged_outputs.jsonl"
)


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-run the LLM judge on all cases"
    )

    args = parser.parse_args()

    # -----------------------------------------------
    # Load input cases
    # -----------------------------------------------

    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        cases = [
            json.loads(line)
            for line in f
        ]

    print(f"Cases to judge: {len(cases)}")

    # -----------------------------------------------
    # Existing results
    # -----------------------------------------------

    results = []

    if OUTPUT_PATH.exists() and not args.force:

        with open(
            OUTPUT_PATH,
            "r",
            encoding="utf-8"
        ) as f:

            results = [
                json.loads(line)
                for line in f
            ]

    completed_ids = {
        r["tweet_id"]
        for r in results
    }

    # -----------------------------------------------
    # Force mode
    # -----------------------------------------------

    if args.force:
        print("\nFORCE MODE: Re-judging all cases.\n")

        results = []
        completed_ids = set()

    # -----------------------------------------------
    # Judge cases
    # -----------------------------------------------

    for i, case in enumerate(cases, 1):

        if case["tweet_id"] in completed_ids:
            continue

        print(
            f"\nJudging {i}/{len(cases)}"
        )

        success = False

        for attempt in range(5):

            try:

                judgment = judge_case(case)

                result = {
                    **case,
                    "llm_reply_quality":
                        judgment["reply_quality"],

                    "llm_escalation":
                        judgment["escalation"],

                    "llm_reason":
                        judgment["reason"],
                }

                results.append(result)

                # Save after every successful case
                with open(
                    OUTPUT_PATH,
                    "w",
                    encoding="utf-8"
                ) as f:

                    for item in results:

                        f.write(
                            json.dumps(
                                item,
                                ensure_ascii=False
                            ) + "\n"
                        )

                print("Saved.")

                success = True
                break

            except Exception as e:

                print(
                    f"Judge failed "
                    f"(attempt {attempt + 1}/5): {e}"
                )

                if attempt < 4:

                    print(
                        "Waiting 15 seconds "
                        "before retry..."
                    )

                    time.sleep(15)

        if not success:

            print(
                "Skipping this case."
            )

            continue

        # Avoid hitting free-tier rate limits
        time.sleep(5)

    # -----------------------------------------------
    # Final output
    # -----------------------------------------------

    print("\n" + "=" * 60)
    print("LLM JUDGE COMPLETE")
    print("=" * 60)

    print(
        f"Judged cases: {len(results)}"
    )

    print(
        f"Output: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()