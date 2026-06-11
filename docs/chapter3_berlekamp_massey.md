# Chapter 3: Berlekamp–Massey Algorithm and Hybrid Detection Model

## 3.1 Mathematical Foundations of the Berlekamp–Massey Algorithm
(Placeholder) Describe linear recurrences, minimal polynomial, and algorithm steps.

## 3.2 Linear Complexity and Anomaly Detection
(Placeholder) Intuition: low linear complexity indicates regular/repetitive structure.

## 3.3 Application of Berlekamp–Massey in Phishing Detection
(Placeholder) Convert URL string to binary sequence and compute linear complexity using `bm_module.berlekamp_massey`.

**Code reference**
- `bm_module.py` — implementation of Berlekamp–Massey used by the pipeline.
- Example: `main.py` and `main_medical.py` call `url_to_binary()` + `berlekamp_massey()` to compute BM score.

## 3.4 Hybrid System Architecture (ML + BM)
(Placeholder) Diagram: text flow → NLP detector; url flow → BM module; decision_engine merges scores.
