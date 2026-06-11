# 🔒 Sistem Hibrid de Detecție a Phishing-ului

## Descriere Proiect

Sistem de detecție a email-urilor de phishing care combină:
- **Machine Learning**: TF-IDF + Random Forest Classifier
- **Criptografie**: Berlekamp-Massey Algorithm pentru analiza URL-urilor

Dezvoltat pentru **disertație academică** - O abordare hibridă bazată pe ML și analiză criptografică.

---

## 📋 Cuprins

1. [Caracteristici Principale](#caracteristici-principale)
2. [Arhitectură Sistem](#arhitectură-sistem)
3. [Instalare și Setup](#instalare-și-setup)
4. [Utilizare](#utilizare)
5. [Evaluare Metrici](#evaluare-metrici)
6. [Documentație Cod](#documentație-cod)
7. [Referințe Academice](#referințe-academice)

---

## ✨ Caracteristici Principale

### 1. **Modul NLP (Natural Language Processing)**
- TF-IDF Vectorization pentru transformarea textului
- Random Forest Classifier (100 estimatori, max_depth=15)
- Detecție cuvinte-cheie de phishing
- Suport fallback pentru medii fără sklearn

### 2. **Modul Berlekamp-Massey**
- Analiza entropiei URL-ului
- Detectare anomalii criptografice
- Scor 0-100 pentru riscul URL-ului

### 3. **Modul de Evaluare (evaluation_module.py)**
- **Metrici de performanță**: Accuracy, Precision, Recall, F1-Score
- **Metrici avansate**: 
  - Matthews Correlation Coefficient (MCC)
  - Cohen's Kappa
  - AUC-ROC
  - Specificity, False Positive Rate, False Negative Rate
- **Confusion Matrix** detaliat
- Optimizare automată de prag

### 4. **Modul de Validare (utils/validation.py)**
- Validare text email
- Validare URL
- Validare dataset
- Preprocessing text
- Extracție caracteristici

### 5. **Logging și Auditare**
- Logging detaliat în `phishing_detection.log`
- Salvare rezultate analize în `analysis_log.jsonl`
- Rapoarte exportabile

---

## 🏗️ Arhitectură Sistem

```
phishing_hybrid_system/
├── app.py                          # Interfață Streamlit (REFACTORIZAT)
├── evaluation_module.py            # Modul metrici și evaluare (NOU)
├── config.py                       # Configurații (ÎMBUNĂTĂȚIT)
├── bm_module.py                    # Berlekamp-Massey Algorithm
├── nlp_module.py                   # NLP Support
├── decision_engine.py              # Motorul de decizie
├── utils/
│   ├── validation.py               # Validare și preprocessing (NOU)
│   └── privacy.py                  # Privacy utilities
├── data/
│   ├── emails.csv                  # Date de antrenament
│   ├── emails_medical.csv          # Date medical
│   └── demo_attack.csv             # Date demo
├── docs/
│   ├── chapter4_implementation.md  # Documentație implementare
│   └── ... (alte documente academice)
└── requirements.txt
```

---

## 🚀 Instalare și Setup

### Prerequisite
- Python 3.8+
- pip

### Pasul 1: Instalare Dependențe
```bash
pip install -r requirements.txt
```

### Pasul 2: Pregătire Date
Asigură-te că `data/emails.csv` conține:
```csv
email_text,label
"Click here to verify your account",1
"Meeting tomorrow at 2pm",0
...
```

Coloane obligatorii:
- `email_text`: Textul emailului
- `label`: 0 (legitimate), 1 (phishing)

### Pasul 3: Rulare Aplicație
```bash
streamlit run app.py
```

Accesează în browser: `http://localhost:8501`

---

## 📖 Utilizare

### Modul Streamlit (app.py)

**Interfață interactivă pentru analiză email:**

1. **Input**:
   - Textul emailului
   - URL din email

2. **Configurare**:
   - NLP Threshold (0.0-1.0, default 0.6)
   - BM Threshold (0-100, default 40)

3. **Output**:
   - Scor NLP cu explicații
   - Scor Berlekamp-Massey
   - Verdict final (PHISHING / LEGITIMATE)
   - Raport exportabil

### Python API

```python
from app import NLPDetector, hybrid_decision
from bm_module import BerlekampMasseyAnalyzer

# Detectare NLP
nlp = NLPDetector()
nlp.train(texts, labels)
nlp_score = nlp.predict("Click here to verify")

# Analiza BM
bm = BerlekampMasseyAnalyzer()
bm_score = bm.analyze_url("https://phishing-site.com")

# Decizie hibridă
verdict = hybrid_decision(nlp_score, bm_score)
```

---

## 📊 Evaluare Metrici

### Modul Evaluare (evaluation_module.py)

```python
from evaluation_module import calculate_metrics, find_optimal_threshold

# Calculare metrici
metrics = calculate_metrics(y_true, y_pred)
print(metrics)

# Optimizare prag
optimal_threshold, optimal_metrics = find_optimal_threshold(
    y_true, 
    y_proba, 
    metric='f1'
)
```

### Metrici Disponibile

| Metrică | Descriere | Formula |
|---------|-----------|---------|
| **Accuracy** | Procent predicții corecte | (TP+TN)/(TP+TN+FP+FN) |
| **Precision** | Corectitudine phishing | TP/(TP+FP) |
| **Recall** | Sensibilitate phishing | TP/(TP+FN) |
| **F1-Score** | Media armonică | 2×(Precision×Recall)/(Precision+Recall) |
| **Specificity** | Corectitudine legitime | TN/(TN+FP) |
| **MCC** | Corelație Matthews | Scalare -1 la 1 |
| **AUC-ROC** | Aria sub curba ROC | Măsură separabilitate |

### Output Exemplu
```
ModelMetrics:
- Accuracy: 0.925
- Precision: 0.910
- Recall: 0.945
- F1-Score: 0.927
- Specificity: 0.905
- False Positive Rate: 0.095
- False Negative Rate: 0.055
- Matthews CC: 0.855
- Cohen's Kappa: 0.850
- AUC-ROC: 0.965
```

---

## 💻 Documentație Cod

### app.py (Refactorizat)

**Componente Principale:**

#### 1. NLPDetector Class
```python
class NLPDetector:
    """Detector NLP cu support ML și fallback token-matching"""
    
    def __init__(self) -> None:
        """Inițializare TF-IDF + Random Forest"""
    
    def train(self, texts: List[str], labels: List[int]) -> None:
        """Antrenament pe date"""
    
    def predict(self, text: str) -> float:
        """Predicție score 0.0-1.0"""
```

#### 2. Funcții Utilitate
```python
@st.cache_resource
def load_training_data() -> Optional[pd.DataFrame]:
    """Încarcă și cachează datele de antrenament"""

@st.cache_resource
def get_trained_nlp_detector(data: pd.DataFrame) -> Optional[NLPDetector]:
    """Obține model antrenat (cached)"""

def evaluate_model(nlp: NLPDetector, data: pd.DataFrame, threshold: float) -> Dict[str, float]:
    """Calculează metrici pe datele de antrenament"""

def log_analysis_result(email_text: str, email_url: str, verdict: str, ...) -> None:
    """Loghează rezultatul în JSONL"""

def hybrid_decision(nlp_score: float, bm_score: float, nlp_thresh: float, bm_thresh: float) -> str:
    """Decizie finală: PHISHING sau LEGITIMATE"""
```

### config.py (Îmbunătățit)

```python
@dataclass
class ModelConfig:
    """Parametri TF-IDF și Random Forest"""
    ngram_range: tuple = (1, 2)
    n_estimators: int = 100
    max_depth: int = 15
    # ...

@dataclass
class ThresholdConfig:
    """Praguri de decizie"""
    nlp_threshold: float = 0.6
    bm_threshold: float = 40.0
    high_security_nlp: float = 0.5
    low_security_nlp: float = 0.7
    # ...

# Configurații Predefinite
HIGH_SECURITY_CONFIG    # Mod strict
BALANCED_CONFIG        # Mod echilibrat
PERFORMANCE_CONFIG     # Mod rapid
```

### evaluation_module.py (NOU)

```python
@dataclass
class ModelMetrics:
    """Container pentru metrici"""
    accuracy: float
    precision: float
    recall: float
    f1: float
    specificity: float
    # ... și altele

def calculate_metrics(y_true, y_pred, y_pred_proba=None) -> ModelMetrics:
    """Calculează metrici comprehensive"""

def find_optimal_threshold(y_true, y_proba, metric='f1') -> Tuple[float, ModelMetrics]:
    """Găsește prag optim"""

def analyze_threshold_impact(y_true, y_proba, thresholds) -> Dict[float, ModelMetrics]:
    """Analizează efectul diferitelor praguri"""
```

### utils/validation.py (NOU)

```python
class DataValidator:
    """Validare date de intrare"""
    @staticmethod
    def validate_email_text(text: str) -> Tuple[bool, str]
    @staticmethod
    def validate_url(url: str) -> Tuple[bool, str]
    @staticmethod
    def validate_dataset(csv_path: Path) -> Tuple[bool, str]

class TextPreprocessor:
    """Preprocesare și extracție caracteristici"""
    @staticmethod
    def clean_text(text: str) -> str
    @staticmethod
    def extract_features(text: str) -> Dict[str, any]
    @staticmethod
    def tokenize(text: str) -> List[str]

class ResultsProcessor:
    """Salvare și procesare rezultate"""
    @staticmethod
    def save_analysis_result(result: Dict, output_file: str) -> bool
    @staticmethod
    def generate_report(results: List[Dict], report_file: str) -> bool
```

---

## 📝 Type Hints Completi

Toate funcțiile includ type hints complete:

```python
def hybrid_decision(nlp_score: float, bm_score: float, nlp_thresh: float = 0.6, bm_thresh: float = 40) -> str:
    """Decizie hibridă cu type hints complete"""
    ...
```

---

## 📋 Logging Sistematic

### Fișiere Log

1. **phishing_detection.log** - Log principal
   ```
   2026-01-14 10:30:45 - app - INFO - NLP Detector initialized with scikit-learn
   2026-01-14 10:30:46 - app - INFO - Loaded 500 training samples
   2026-01-14 10:31:00 - app - INFO - Model evaluation - F1: 0.925, Accuracy: 0.930
   ```

2. **analysis_log.jsonl** - Rezultate analize
   ```json
   {"timestamp": "2026-01-14T10:35:22", "verdict": "PHISHING", "nlp_score": 0.75, "bm_score": 45.5, "email_url": "https://phishing.com", "text_length": 245}
   ```

---

## 🔗 Referințe Academice

### Machine Learning
- TF-IDF Vectorization: Text Mining Literature
- Random Forest: Breiman, L. (2001). "Machine Learning"
- Feature Extraction: Goodfellow et al. (2016). "Deep Learning"

### Criptografie
- Berlekamp-Massey Algorithm: Berlekamp, E.R., Massey, J.L. (1968)
- Linear Feedback Shift Registers: Golomb, S.W. (1967)
- Entropy Analysis: Shannon, C.E. (1948)

### Phishing Detection
- APWG: Anti-Phishing Working Group (https://apwg.org/)
- Phishing Trends: APWG Global Phishing Survey
- Email Security: RFC 5322, RFC 6854

---

## 📊 Rezultate Experimentale Așteptate

(Exemplu pentru disertație)

| Model | Accuracy | Precision | Recall | F1-Score | AUC-ROC |
|-------|----------|-----------|--------|----------|---------|
| NLP Only | 0.885 | 0.875 | 0.895 | 0.885 | 0.940 |
| BM Only | 0.745 | 0.720 | 0.800 | 0.758 | 0.810 |
| **Hybrid** | **0.930** | **0.920** | **0.945** | **0.932** | **0.965** |

---

## 🛠️ Troubleshooting

### Problema: "sklearn not available"
**Soluție:**
```bash
pip install scikit-learn
```

### Problema: "File not found: data/emails.csv"
**Soluție:** Creează CSV cu structura corectă:
```csv
email_text,label
"Your text here",0
```

### Problema: "CSV missing required columns"
**Soluție:** Asigură-te că CSV are coloane: `email_text`, `label`

---

## 📞 Contact & Support

Pentru întrebări referitoare la disertație, contactează:
- Repository: Phishing Detection Hybrid System
- Documentație: `docs/` folder
- Tests: `tests/` folder

---

## 📄 Licență

Proiect academic - Disertație Universitate
Data: 2026
Versiune: 1.0.0

---

**Ultima actualizare:** 2026-01-14
