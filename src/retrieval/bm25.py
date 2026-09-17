import json
import re
from pathlib import Path

from rank_bm25 import BM25Okapi


class BM25Retriever:

    def __init__(self, cases_path):
        self.cases_path = Path(cases_path)

        self.cases = []
        self.documents = []
        self.tokenized_documents = []

        self._load_cases()
        self._build_index()

    def _tokenize(self, text):
        return re.findall(r"\b\w+\b", text.lower())

    def _load_cases(self):
        with open(self.cases_path, "r", encoding="utf-8") as f:
            for line in f:
                case = json.loads(line)

                customer_messages = [
                    message["text"]
                    for message in case["messages"]
                    if message["speaker"] == "customer"
                ]

                support_messages = [
                    message
                    for message in case["messages"]
                    if message["speaker"] == "AppleSupport"
                ]

                if not customer_messages:
                    continue

                customer_text = " ".join(customer_messages)

                self.cases.append({
                    "conversation_id": case["conversation_id"],
                    "customer_text": customer_text,
                    "support_messages": support_messages,
                    "messages": case["messages"]
                })

                self.documents.append(customer_text)
                self.tokenized_documents.append(
                    self._tokenize(customer_text)
                )

    def _build_index(self):
        self.bm25 = BM25Okapi(self.tokenized_documents)

    def search(self, query, top_k=5):

        query_tokens = self._tokenize(query)

        scores = self.bm25.get_scores(query_tokens)

        ranked_indices = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True
        )[:top_k]

        results = []

        for index in ranked_indices:
            case = self.cases[index]

            results.append({
                "conversation_id": case["conversation_id"],
                "customer_text": case["customer_text"],
                "support_messages": case["support_messages"],
                "score": float(scores[index])
            })

        return results