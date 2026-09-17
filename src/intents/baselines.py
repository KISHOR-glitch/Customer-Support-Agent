from collections import Counter


def get_majority_intent(labels):
    counts = Counter(labels)
    return counts.most_common(1)[0][0]


def predict_majority(text, majority_intent):
    return majority_intent