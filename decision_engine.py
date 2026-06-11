# Default thresholds
NLP_THRESHOLD = 0.6
BM_THRESHOLD = 40


def hybrid_decision(nlp_score, bm_score, nlp_thresh=NLP_THRESHOLD, bm_thresh=BM_THRESHOLD):
    """
    Decizie finală bazată pe ambii senzori.
    
    Args:
        nlp_score: Probabilitate NLP de phishing (0-1)
        bm_score: Complexitate liniară URL (0-100)
        nlp_thresh: NLP threshold
        bm_thresh: BM threshold
    
    Returns:
        "PHISHING" sau "LEGITIMATE"
    """
    # Phishing detectat dacă:
    # - NLP score e ridicat (> threshold) ȘI
    # - URL are pattern-uri regulate (< threshold pentru BM)
    if nlp_score > nlp_thresh or bm_score < bm_thresh:
        return "PHISHING"
    return "LEGITIMATE"
