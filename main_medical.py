"""
Medical phishing detection pipeline (Epic, Cerner, Medidata)
"""
import csv
import sys
from nlp_module import NLPDetector  # type: ignore
from bm_module import berlekamp_massey, url_to_binary  # type: ignore
from decision_engine import hybrid_decision  # type: ignore
from analyzers.epic_analyzer import EpicAnalyzer  # type: ignore
from analyzers.cerner_analyzer import CernerAnalyzer  # type: ignore
from analyzers.medidata_analyzer import MedidataAnalyzer  # type: ignore

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

def main_medical():
    try:
        # Load medical dataset
        print("[1] Încarcă dataset medical...")
        texts, labels, urls, software_types = load_csv("data/emails_medical.csv")
        
        print(f"    ✓ Dataset încărcat: {len(texts)} email-uri medicale\n")
        
        # Analyze medical emails with software-specific analyzers
        print("[2] Analiziază email-urile medicale cu analizoare specifice...")
        print("-" * 70)
        
        results = []
        for i in range(len(texts)):
            software = software_types[i].lower() if i < len(software_types) else 'generic'
            analyzer = ANALYZERS.get(software)
            
            if analyzer:
                nlp_score, bm_score, verdict = analyzer.analyze(texts[i], urls[i])
            else:
                # Fallback to generic
                nlp_score = 0.0
                bm_score = 0
                verdict = "UNKNOWN"
            
            results.append({
                "email_id": i + 1,
                "software": software.upper(),
                "nlp_score": round(nlp_score, 3),
                "bm_score": bm_score,
                "verdict": verdict
            })
            
            print(f"Email {i+1:2d} [{software:8s}]: NLP={nlp_score:.3f} | BM={bm_score:3d} | {verdict}")
        
        print("-" * 70)
        print(f"\n[3] Rezultate finale:")
        phishing_count = sum(1 for r in results if r["verdict"] == "PHISHING")
        legitimate_count = sum(1 for r in results if r["verdict"] == "LEGITIMATE")
        print(f"    PHISHING: {phishing_count}")
        print(f"    LEGITIMATE: {legitimate_count}")
        
        # Summary by software
        print(f"\n[4] Analiză per software:")
        for soft in ['EPIC', 'CERNER', 'MEDIDATA']:
            soft_results = [r for r in results if r['software'] == soft]
            if soft_results:
                soft_phishing = sum(1 for r in soft_results if r["verdict"] == "PHISHING")
                print(f"    {soft}: {len(soft_results)} emails, {soft_phishing} phishing")
        
        return results
        
    except Exception as e:
        print(f"❌ Eroare: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main_medical()
