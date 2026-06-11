"""Epic EHR Phishing Analyzer"""
import re

class EpicAnalyzer:
    """Detectează phishing specific pentru Epic EHR systems"""

    EPIC_KEYWORDS = {
        'epic': 1.5,
        'epic login': 3.0,
        'epic credentials': 3.0,
        'epic access': 2.5,
        'verify epic': 2.5,
        'epic password': 3.0,
        'epic portal': 2.0,
        'epic account': 2.5,
        'mychart': 2.5,
        'patient portal': 2.0,
        'update clinic': 1.5,
    }

    def analyze(self, text, url):
        """Returnează (nlp_score, bm_score, verdict)"""
        nlp_score = self._calculate_nlp_score(text)
        bm_score = self._calculate_bm_score(url)
        verdict = self._make_decision(nlp_score, bm_score)
        return nlp_score, bm_score, verdict

    def _calculate_nlp_score(self, text):
        """Detecție NLP specifică Epic"""
        if not text:
            return 0.0

        text_lower = text.lower()
        score = 0.0

        # Cuvinte cheie
        for keyword, weight in self.EPIC_KEYWORDS.items():
            if keyword in text_lower:
                score += weight

        # Pattern-uri Epic suspecte
        epic_patterns = [
            r'https?://.*epic.*',
            r'https?://.*mychart.*',
            r'https?://.*patient.*portal.*',
            r'bit\.ly|tinyurl',  # URL shorteners
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',  # IP addresses
        ]

        for pattern in epic_patterns:
            if re.search(pattern, text_lower):
                score += 1.5

        return min(score / 8.0, 1.0)

    def _calculate_bm_score(self, url):
        """BM score din URL"""
        if not url:
            return 100

        # Conversie URL la binary
        binary_seq = [int(bit) for char in url for bit in format(ord(char), '08b')]

        # Simplified BM: return length
        return len(binary_seq)

    def _make_decision(self, nlp_score, bm_score):
        """Decizie Epic-specific: NLP threshold 0.5, BM threshold 100"""
        if nlp_score > 0.5 or bm_score < 100:
            return "PHISHING"
        return "LEGITIMATE"
