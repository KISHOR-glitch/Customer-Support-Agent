from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression


class SemanticClassifier:

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2),
            min_df=2,
            max_features=20000
        )

        self.model = LogisticRegression(
            max_iter=1000,
            class_weight="balanced"
        )

    def train(self, texts, labels):
        X = self.vectorizer.fit_transform(texts)
        self.model.fit(X, labels)

    def predict(self, text):
        X = self.vectorizer.transform([text])

        prediction = self.model.predict(X)[0]

        probabilities = self.model.predict_proba(X)[0]
        confidence = probabilities.max()

        return prediction, confidence