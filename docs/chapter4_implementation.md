# Chapter 4: System Implementation and Experimental Evaluation

## 4.1 Dataset Description and Preprocessing
- Datasets are in `data/`:
  - `emails.csv` — generic examples
  - `emails_medical.csv` — medical-targeted examples
  - `demo_attack.csv` — demo dataset used in this project

- Preprocessing: `main.py` and `main_medical.py` use a simple CSV loader and lightweight feature extraction. Replace with full preprocessing (pandas, sklearn) if dependencies are available.

## 4.2 Software Architecture and Development Environment
- Python 3.10 (project used virtual environment `venv`)
- Key modules:
  - `nlp_module.py` — NLP detector
  - `bm_module.py` — Berlekamp–Massey
  - `decision_engine.py` — hybrid rules
  - `analyzers/` — per-software analyzers for Epic/Cerner/Medidata
  - `integrations/` — SIEM and email gateway helpers

## 4.3 Implementation of Detection Modules
- `nlp_module.py`: keyword-based fallback; can be replaced with TF-IDF + LogisticRegression.
- `bm_module.py`: sequence conversion and `berlekamp_massey` implementation.

Sample snippet (from `bm_module.py`):

```python
binary_seq = url_to_binary(url)
bm_score = berlekamp_massey(binary_seq)
```

## 4.4 Experimental Results and Performance Evaluation
- Run the demo: `python run_demo.py`
- Demo report saved to `reports/demo_results.csv` (created by the demo run).
- Metrics to collect: TP, FP, TN, FN, precision, recall; collect more labeled examples for robust evaluation.
