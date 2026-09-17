import json

path = "data/golden/human_eval_outputs.jsonl"

with open(path, "r", encoding="utf-8") as f:
    data = [json.loads(line) for line in f]

errors = [
    x for x in data
    if x["gold_intent"] != x["predicted_intent"]
]

print("=" * 70)
print(f"INTENT ERRORS: {len(errors)}")
print("=" * 70)

for i, x in enumerate(errors, 1):
    print(f"\n{i}. {x['customer_message']}")
    print(f"   Gold      : {x['gold_intent']}")
    print(f"   Predicted : {x['predicted_intent']}")