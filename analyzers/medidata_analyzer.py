"""Medidata CDMS Phishing Analyzer"""
import re


class MedidataAnalyzer:
    """Detectează phishing pentru Medidata Clinical Data Management"""
    
    MEDIDATA_KEYWORDS = {
        'medidata': 1.5,
        'medidata login': 3.0,
        'clinical trial': 2.0,
        'patient data': 2.5,
        'trial data': 2.5,
        'verify medidata': 2.5,
        'medidata credentials': 3.0,
        'rave edc': 2.0,
        'clinical database': 2.0,
        'study data': 1.5,
    }
    
    def analyze(self, text, url):
        """Returnează (nlp_score, bm_score, verdict)"""
        nlp_score = self._calculate_nlp_score(text)
        bm_score = self._calculate_bm_score(url)
        verdict = self._make_decision(nlp_score, bm_score)
        return nlp_score, bm_score, verdict
    
    def _calculate_nlp_score(self, text):
        """Detecție NLP specifică Medidata"""
        if not text:
            return 0.0
        
        text_lower = text.lower()
        score = 0.0
        
        # Cuvinte cheie
        for keyword, weight in self.MEDIDATA_KEYWORDS.items():
            if keyword in text_lower:
                score += weight
        
        # Pattern-uri Medidata suspecte
        medidata_patterns = [
            r'https?://.*medidata.*',
            r'https?://.*rave.*',
            r'https?://.*clinical.*trial.*',
            r'bit\.ly|tinyurl',
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',
        ]
        
        for pattern in medidata_patterns:
            if re.search(pattern, text_lower):
                score += 1.5
        
        return min(score / 8.0, 1.0)
    
    def _calculate_bm_score(self, url):
        """BM score din URL"""
        if not url:
            return 100
        
        binary_seq = [int(bit) for char in url for bit in format(ord(char), '08b')]
        return len(binary_seq)
    
    def _make_decision(self, nlp_score, bm_score):
        """Decizie Medidata-specific"""
        if nlp_score > 0.5 or bm_score < 100:
            return "PHISHING"
        return "LEGITIMATE"
