"""Demo runner: simulate an attack dataset and show detection + mitigation guidance."""
import csv
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nlp_module import NLPDetector # pyright: ignore[reportMissingImports]
from bm_module import berlekamp_massey, url_to_binary # type: ignore
from decision_engine import hybrid_decision # type: ignore
from analyzers.epic_analyzer import EpicAnalyzer # pyright: ignore[reportMissingImports]
from analyzers.cerner_analyzer import CernerAnalyzer # type: ignore
from analyzers.medidata_analyzer import MedidataAnalyzer # type: ignore
from integrations.siem import send_alert # pyright: ignore[reportMissingImports]
from integrations.email_gateway import append_blocklist # pyright: ignore[reportMissingImports]
from utils.privacy import redact # type: ignore

ANALYZERS = {
    'epic': EpicAnalyzer(),
    'cerner': CernerAnalyzer(),
    'medidata': MedidataAnalyzer(),
}

DEMO_PATH = 'data/demo_attack.csv'


def load_csv(filepath):
    rows = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for r in reader:
                rows.append(r)
    except Exception as e:
        print('Error loading CSV:', e)
        sys.exit(1)
    return rows
    """Load CSV file and return list of dictionaries."""


def recommend_action(verdict, nlp_score, bm_score, url, software):
    actions = []
    if verdict == 'PHISHING':
        actions.append('Quarantine the email')
        actions.append('Block the URL at gateway/firewall')
        actions.append('Notify security/IT and affected users')
    else:
        if nlp_score > 0.5:
            actions.append('Flag for human review')
        else:
            actions.append('No immediate action; monitor')
    # specific extra guidance for medical targets
    if software and software.lower() in ('epic', 'cerner', 'medidata') and verdict == 'PHISHING':
        actions.append('Run incident response for medical systems and check EHR access logs')
    """Generate recommended actions based on detection results."""
    # show URL-specific guidance
    if url and ('bit.ly' in url or 'tinyurl' in url):
        actions.append('Resolve shortened URL via safe resolver before clicking')
    return actions


def run_demo(path=DEMO_PATH):
    """Run the phishing detection demo on the attack dataset."""
    print('\n' + '='*80)
    print('PHISHING HYBRID DETECTION SYSTEM - DEMO')
    print('='*80)
    print(f'\nDemo dataset: {path}')
    rows = load_csv(path)
    print(f'Loaded {len(rows)} emails from demo dataset')

    nlp = NLPDetector()
    texts = [r.get('email_text','') for r in rows]
    labels = [int(r.get('label',0)) for r in rows]
    nlp.train(texts, labels)
    print(f'NLP detector trained on {len(texts)} samples')

    print('\n' + '-'*80)
    print('Running detection on demo emails...')
    print('-'*80)
    results = []
    for i,r in enumerate(rows, start=1):
        text = r.get('email_text','')
        url = r.get('url','')
        software = r.get('software_type','generic')

        # Redact sensitive information in the email text
        redacted_text = redact(text)

        # if we have a software-specific analyzer, use it
        analyzer = ANALYZERS.get(software.lower()) if software else None
        
        try:
            if analyzer:
                nlp_score, bm_score, verdict = analyzer.analyze(redacted_text, url)
            else:
                nlp_score = nlp.predict(redacted_text)
                binary_seq = url_to_binary(url)
                bm_score = berlekamp_massey(binary_seq)
                verdict = hybrid_decision(nlp_score, bm_score)
        except Exception as e:
            print(f"Error analyzing email {i}: {e}")
            nlp_score = nlp.predict(redacted_text)
            binary_seq = url_to_binary(url)
            bm_score = berlekamp_massey(binary_seq)
            verdict = hybrid_decision(nlp_score, bm_score)
        else:
            nlp_score = nlp.predict(redacted_text)
            binary_seq = url_to_binary(url)
            bm_score = berlekamp_massey(binary_seq)
            verdict = hybrid_decision(nlp_score, bm_score)

        actions = recommend_action(verdict, nlp_score, bm_score, url, software)

        # Redact text for logs/reports by default
        print(f"Email {i:2d} [{software:8s}]")
        print('  Text:', redacted_text[:120])
        print(f"  URL: {url}")
        print(f"  NLP score: {nlp_score:.3f}, BM score: {bm_score}, Verdict: {verdict}")
        print('  Recommended actions:')
        for a in actions:
            print('   -', a)
        print('-' * 80)
        ''

        # Integrations: send alert and append blocklist on PHISHING
        if verdict == 'PHISHING':
            alert = {
                'id': i,
                'software': software,
                'nlp_score': nlp_score,
                'bm_score': bm_score,
                'url': url,
                'text_snippet': redacted_text[:500]
            }
            alert = {
                'email_id': i,
                'software': software,
                'nlp_score': nlp_score,
                'bm_score': bm_score,
                'url': url,
                'text_snippet': redacted_text[:500],
                'recommended_actions': actions
            }
            try:
                send_alert(alert)
            except Exception as e:
                print(f'  [SIEM] Alert not sent: {e}')
            
            try:
                if url:
                    append_blocklist(url)
                    print(f'  [GATEWAY] Added to blocklist: {url}')
            except Exception as e:
                print(f'  [GATEWAY] Blocklist update failed: {e}')

        results.append({
            'id': i,
            'software': software,
            'nlp_score': nlp_score,
            'bm_score': bm_score,
            'verdict': verdict,
            'actions': actions,
        })

    # summary
    # Print summary
    print('\n' + '-'*80)
    phishing_count = sum(1 for x in results if x['verdict'] == 'PHISHING')
    legitimate_count = len(results) - phishing_count
    
    print(f'\nSUMMARY:')
    print(f"  Phishing detected: {phishing_count}/{len(results)}")
    print(f"  Legitimate: {legitimate_count}/{len(results)}")
    print(f"  Detection rate: {phishing_count/len(results)*100:.1f}%")
    print('='*80 + '\n')
    
    return results


if __name__ == '__main__':
    results = run_demo()
