import re
class CernerAnalyzer:
    """Detectează phishing specific pentru Cerner systems"""
    
    CERNER_KEYWORDS = {
        'cerner': 1.5,
        'cerner login': 3.0,
        'cerner credentials': 3.0,
        'cerner access': 2.5,
        'verify cerner': 2.5,
        'cerner password': 3.0,
        'cerner ehr': 2.5,
        'powerchart': 2.5,
        'millennium': 2.0,
        'cerner account': 2.5,
        'ehr access': 2.0,
    }
    
    def analyze(self, text, url):
        """Returnează (nlp_score, bm_score, verdict)"""
        nlp_score = self._calculate_nlp_score(text)
        bm_score = self._calculate_bm_score(url)
        verdict = self._make_decision(nlp_score, bm_score)
        return nlp_score, bm_score, verdict
    
    def _calculate_nlp_score(self, text):
        """Detecție NLP specifică Cerner"""
        if not text:
            return 0.0
        
        text_lower = text.lower()
        score = 0.0
        
        # Cuvinte cheie
        for keyword, weight in self.CERNER_KEYWORDS.items():
            if keyword in text_lower:
                score += weight
        
        # Pattern-uri Cerner suspecte
        cerner_patterns = [
            r'https?://.*cerner.*',
            r'https?://.*powerchart.*',
            r'https?://.*millennium.*',
            r'bit\.ly|tinyurl',
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',
        ]
        
        for pattern in cerner_patterns:
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
        """Decizie Cerner-specific"""
        if nlp_score > 0.5 or bm_score < 100:
            return "PHISHING"
        return "LEGITIMATE"
