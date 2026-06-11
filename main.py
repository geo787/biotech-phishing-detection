import csv
import sys
from nlp_module import NLPDetector # pyright: ignore[reportMissingImports]
from bm_module import berlekamp_massey, url_to_binary # pyright: ignore[reportMissingImports]
from decision_engine import hybrid_decision # type: ignore
from analyzers.epic_analyzer import EpicAnalyzer # type: ignore
from analyzers.cerner_analyzer import CernerAnalyzer # type: ignore
from analyzers.medidata_analyzer import MedidataAnalyzer # type: ignore
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# Analizoare specifice pentru software-uri medicale
ANALYZERS = {
    'epic': EpicAnalyzer(),
    'cerner': CernerAnalyzer(),
    'medidata': MedidataAnalyzer(),
}

def load_csv(filepath):
    texts, labels, urls, software_types = [], [], [], []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                texts.append(row.get('email_text', ''))
                labels.append(int(row.get('label', 0)))
                urls.append(row.get('url', ''))
                software_types.append(row.get('software_type', 'generic'))
    except Exception as e:
        print(f"❌ Eroare citire CSV: {e}")
    return texts, labels, urls, software_types

def main():
    try:
        # Load dataset
        print("[1] Încarcă dataset...")
        texts, labels, urls, software_types = load_csv("data/emails.csv") # type: ignore
        
        print(f"    ✓ Dataset încărcat: {len(texts)} email-uri\n")
        
        # Train NLP model
        print("[2] Antrenează modelul NLP...")
        nlp = NLPDetector()
        nlp.train(texts, labels)
        print("    ✓ Model NLP antrenat\n")
        
        # Analyze emails
        print("[3] Analiziază email-urile...")
        print("-" * 60)
        
        results = []
        for i in range(len(texts)):
            # If we have a software-specific analyzer, use it
            software = software_types[i] if i < len(software_types) else 'generic'
            if software and software.lower() in ANALYZERS:
                analyzer = ANALYZERS[software.lower()]
                try:
                    nlp_score, bm_score, verdict = analyzer.analyze(texts[i], urls[i])
                except Exception:
                    # fallback to generic pipeline on analyzer error
                    nlp_score = nlp.predict(texts[i])
                    binary_seq = url_to_binary(urls[i])
                    bm_score = berlekamp_massey(binary_seq)
                    verdict = hybrid_decision(nlp_score, bm_score)
            else:
                # NLP score
                nlp_score = nlp.predict(texts[i])

                # Berlekamp-Massey score
                binary_seq = url_to_binary(urls[i])
                bm_score = berlekamp_massey(binary_seq)

                # Hybrid decision
                verdict = hybrid_decision(nlp_score, bm_score)
            
            results.append({
                "email_id": i + 1,
                "nlp_score": round(nlp_score, 3),
                "bm_score": bm_score,
                "verdict": verdict
            })
            
            print(f"Email {i+1:2d}: NLP={nlp_score:.3f} | BM={bm_score:3d} | {verdict}")
        
        print("-" * 60)
        print(f"\n[4] Rezultate finale:")
        phishing_count = sum(1 for r in results if r["verdict"] == "PHISHING")
        legitimate_count = len(results) - phishing_count
        print(f"    PHISHING: {phishing_count}")
        print(f"    LEGITIMATE: {legitimate_count}")
        
        # Feature extraction and model training for ensemble method
        vectorizer = TfidfVectorizer(ngram_range=(1,2), max_features=20000)
        X = vectorizer.fit_transform(texts)  # texts: list[str]
        y = labels                            # labels: list[int]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        clf = RandomForestClassifier(n_estimators=100, random_state=42)
        clf.fit(X_train, y_train)
        probs = clf.predict_proba(X_test)[:, 1]
        preds = clf.predict(X_test)
        
        return results        
    except Exception as e:
        print(f"❌ Eroare: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()