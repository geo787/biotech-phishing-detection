```bash
# Instalare dependențe
pip install -r requirements.txt

# Verificare dataset
python -c "from utils.validation import DataValidator; DataValidator.validate_dataset(__import__('pathlib').Path('data/emails.csv'))"
```

### 2. Rulare Aplicație
```bash
streamlit run app.py
```

Acces: `http://localhost:8501`

---

## 💻 API PYTHON RAPID

### Detecție NLP
```python
from app import NLPDetector, get_trained_nlp_detector, load_training_data
import pandas as pd

# Încarcă date
data = load_training_data()

# Obține model antrenat
nlp = get_trained_nlp_detector(data)

# Predicție
score = nlp.predict("Click here to verify your account")
print(f"NLP Score: {score:.3f}")  # 0.000 - 1.000
```

### Analiza URL
```python
from bm_module import BerlekampMasseyAnalyzer

bm = BerlekampMasseyAnalyzer()
score = bm.analyze_url("https://example.com")
print(f"BM Score: {score:.1f}")  # 0 - 100
```

### Decizie Hibridă
```python
from app import hybrid_decision

verdict = hybrid_decision(
    nlp_score=0.75,
    bm_score=45.5,
    nlp_thresh=0.6,
    bm_thresh=40
)
print(verdict)  # "PHISHING" sau "LEGITIMATE"
```

### Evaluare Metrici
```python
from evaluation_module import calculate_metrics, find_optimal_threshold

# Calcul metrici
metrics = calculate_metrics(y_true=[0, 1, 1, 0], y_pred=[0, 1, 0, 0])
print(f"F1-Score: {metrics.f1:.3f}")
print(f"Precision: {metrics.precision:.3f}")
print(f"Recall: {metrics.recall:.3f}")

# Prag optim
optimal_thresh, optimal_metrics = find_optimal_threshold(
    y_true, y_proba, metric='f1'
)
print(f"Optimal threshold: {optimal_thresh}")
```

### Validare Date
```python
from utils.validation import DataValidator, TextPreprocessor

# Validare email
valid, msg = DataValidator.validate_email_text("Click here now!")
print(f"Valid: {valid}, Message: {msg}")

# Validare URL
valid, msg = DataValidator.validate_url("https://example.com")
print(f"Valid: {valid}, Message: {msg}")

# Preprocessing text
clean = TextPreprocessor.clean_text("Click HERE!!! Visit https://example.com")
print(clean)  # "click visit"

# Extracție caracteristici
features = TextPreprocessor.extract_features("Click here now")
print(features)  # {'length': ..., 'word_count': ..., 'urgent_keywords': ...}
```

---

## 📊 METRICI DISPONIBILE

### Metrici de Bază
| Metrică | Definiție | Interpretare |
|---------|-----------|--------------|
| **Accuracy** | (TP+TN)/(Total) | % predicții corecte |
| **Precision** | TP/(TP+FP) | % phishing real din detectate |
| **Recall** | TP/(TP+FN) | % phishing detectate |
| **F1-Score** | 2×(P×R)/(P+R) | Media armonică P şi R |

### Metrici Avansate
| Metrică | Notație | Interpretare |
|---------|---------|--------------|
| **Specificity** | TN/(TN+FP) | % legitime corecte |
| **FPR** | FP/(FP+TN) | % false alarms |
| **FNR** | FN/(FN+TP) | % phishing ratat |
| **MCC** | -1 to 1 | Corela. Matthews |
| **Kappa** | -1 to 1 | Cohen's Kappa |
| **AUC-ROC** | 0 to 1 | Aria sub curba ROC |

---

## 🔧 CONFIGURAȚII PREDEFINITE

### Mod Strict (High Security)
```python
from config import HIGH_SECURITY_CONFIG

config = HIGH_SECURITY_CONFIG
# NLP Threshold: 0.5 (mai sensibil)
# BM Threshold: 35.0 (mai strict)
# Random Forest: 150 estimatori, depth 20
```

### Mod Echilibrat (Balanced)
```python
from config import BALANCED_CONFIG

config = BALANCED_CONFIG
# NLP Threshold: 0.6 (default)
# BM Threshold: 40.0 (default)
# Random Forest: 100 estimatori, depth 15
```

### Mod Performanță (Performance)
```python
from config import PERFORMANCE_CONFIG

config = PERFORMANCE_CONFIG
# NLP Threshold: 0.7 (mai permisiv)
# BM Threshold: 50.0 (mai permisiv)
# Random Forest: 50 estimatori, depth 10
```

---

## 📁 STRUCTURĂ FIȘIERE IMPORTANTE

```
phishing_hybrid_system/
├── app.py                    ← MAIN: Interfață Streamlit
├── evaluation_module.py      ← METRICI: Calcul performanță
├── config.py                 ← SETĂRI: Configurații
├── bm_module.py             ← ALGORITM: Berlekamp-Massey
├── utils/validation.py      ← VALIDARE: Preprocessing
├── data/emails.csv          ← DATASET: Date antrenament
├── README_DISERTATIE.md     ← DOCS: Documentație completă
└── phishing_detection.log   ← LOGGING: Fișier log
```

---

## 🎯 WORKFLOW TIPIC DISERTAȚIE

### 1. Preparare Date
```python
from utils.validation import DataValidator
from pathlib import Path

# Validare dataset
valid, msg = DataValidator.validate_dataset(Path('data/emails.csv'))
assert valid, f"Dataset invalid: {msg}"
```

### 2. Antrenament Model
```python
from app import load_training_data, get_trained_nlp_detector

data = load_training_data()
nlp = get_trained_nlp_detector(data)
```

### 3. Evaluare Model
```python
from evaluation_module import calculate_metrics

# Pe date de test
metrics = calculate_metrics(y_true_test, y_pred_test)

# Print rezultate
print(f"""
REZULTATE EVALUARE:
- Accuracy: {metrics.accuracy:.3f}
- Precision: {metrics.precision:.3f}
- Recall: {metrics.recall:.3f}
- F1-Score: {metrics.f1:.3f}
- AUC-ROC: {metrics.auc_roc:.3f}
""")
```

### 4. Optimizare Praguri
```python
from evaluation_module import find_optimal_threshold

optimal_thresh, optimal_metrics = find_optimal_threshold(
    y_true_test, 
    y_proba_test, 
    metric='f1'
)

print(f"Optimal NLP Threshold: {optimal_thresh}")
print(f"F1-Score at optimal: {optimal_metrics.f1:.3f}")
```

### 5. Analiză Emailuri
```python
from app import hybrid_decision
from bm_module import BerlekampMasseyAnalyzer

# Text exemplu
email_text = "Click here to verify your account urgently!"
email_url = "https://phishing-site.com"

# Analiză
nlp_score = nlp.predict(email_text)
bm = BerlekampMasseyAnalyzer()
bm_score = bm.analyze_url(email_url)

# Decizie
verdict = hybrid_decision(nlp_score, bm_score)

print(f"NLP Score: {nlp_score:.3f}")
print(f"BM Score: {bm_score:.1f}")
print(f"Verdict: {verdict}")
```

### 6. Export Rezultate
```python
from app import log_analysis_result

log_analysis_result(
    email_text=email_text,
    email_url=email_url,
    verdict=verdict,
    nlp_score=nlp_score,
    bm_score=bm_score
)

# Rezultatele sunt salvate în analysis_log.jsonl
```

---

## 📋 CHECKLIST DISERTAȚIE

- [ ] Dataset valid (500+ emailuri)
- [ ] Model antrenat și evaluat
- [ ] Metrici calculate (Accuracy, Precision, Recall, F1, AUC)
- [ ] Praguri optimizate
- [ ] Rezultate logate
- [ ] Raport generat
- [ ] Documentație completă
- [ ] Cod fără erori
- [ ] Tests implementate
- [ ] Reproducibilitate verificată

---

## 🆘 TROUBLESHOOTING RAPID

### Problem: "Module not found"
```bash
pip install -r requirements.txt
```

### Problem: "File not found: data/emails.csv"
```bash
# Creează CSV-ul cu structura corectă
python -c "
import pandas as pd
df = pd.DataFrame({
    'email_text': ['Click here', 'Meeting tomorrow'],
    'label': [1, 0]
})
df.to_csv('data/emails.csv', index=False)
"
```

### Problem: "sklearn not available"
```bash
pip install scikit-learn
```

### Problem: "Streamlit errors"
```bash
pip install streamlit --upgrade
streamlit run app.py --logger.level=debug
```

---

## 📊 FORMULE METRICI

```
TP = True Positives (phishing detectat corect)
FP = False Positives (legitimate detectat ca phishing)
TN = True Negatives (legitimate detectat corect)
FN = False Negatives (phishing ratat)

Accuracy = (TP + TN) / (TP + FP + FN + TN)
Precision = TP / (TP + FP)
Recall = TP / (TP + FN)
F1 = 2 × (Precision × Recall) / (Precision + Recall)
Specificity = TN / (TN + FP)
FPR = FP / (FP + TN)
FNR = FN / (FN + TP)
```

---

## 🔗 REFERINȚE RAPIDE

- **Documentație Completă:** README_DISERTATIE.md
- **Refactoring Summary:** REFACTORING_SUMMARY.md
- **Logs:** phishing_detection.log
- **Rezultate:** analysis_log.jsonl
- **Configurații:** config.py

---

**Tip:** Pentru debugging, utilizează:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
```

**Data:** 14.01.2026 | **Versiune:** 1.0.0
