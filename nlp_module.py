from typing import List

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.ensemble import RandomForestClassifier
    _sklearn_available = True
except Exception:
    TfidfVectorizer = None  # type: ignore
    RandomForestClassifier = None  # type: ignore
    _sklearn_available = False

SUSPICIOUS_TOKENS = [
    "urgent", "verify", "click", "account", "password", "login", "bank",
    "update", "confirm", "security", "ssn", "social", "bit.ly",
    "tinyurl", "paypal", "invoice", "wire", "transfer"
]

class NLPDetector:
    def __init__(self):
        self._is_trained = False
        if _sklearn_available and TfidfVectorizer is not None and RandomForestClassifier is not None:
            self.vectorizer = TfidfVectorizer(
                ngram_range=(1, 2),
                max_features=20000,
                stop_words="english",
                min_df=2,
                max_df=0.95,
            )
            self.clf = RandomForestClassifier(n_estimators=100, max_depth=15, random_state=42)
        else:
            self._token_set = set(SUSPICIOUS_TOKENS)

    def train(self, texts: List[str], labels: List[int]) -> None:
        if _sklearn_available:
            self.vectorizer.fit(texts)
            X = self.vectorizer.transform(texts)
            self.clf.fit(X, labels)
            self._is_trained = True
        else:
            phishing_tokens = {}
            for text, label in zip(texts, labels):
                if label:
                    for tok in text.lower().split():
                        if len(tok) > 2:
                            phishing_tokens[tok] = phishing_tokens.get(tok, 0) + 1
            top = sorted(phishing_tokens.items(), key=lambda x: -x[1])[:50]
            for tok, _ in top:
                self._token_set.add(tok)

    def predict(self, text: str) -> float:
        if _sklearn_available and self._is_trained:
            X = self.vectorizer.transform([text])
            proba = self.clf.predict_proba(X)[0][1]
            return float(proba)
        text_l = text.lower()
        tokens = text_l.split()
        if not tokens:
            return 0.0
        hits = sum(1 for t in tokens if any(st in t for st in self._token_set))
        score = hits / max(1, len(tokens))
        return min(1.0, score * 2.0)

__all__ = ["NLPDetector"]