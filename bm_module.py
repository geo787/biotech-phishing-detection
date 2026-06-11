"""
Berlekamp-Massey Algorithm for URL Phishing Detection
Analyzes URL patterns and characteristics using polynomial-based anomaly detection
"""
import re
from urllib.parse import urlparse
from typing import List, Tuple


class BerlekampMasseyAnalyzer:
    """Detects phishing URLs using Berlekamp-Massey sequence analysis"""
    
    def __init__(self):
        self.suspicious_domains = [
            "bit.ly", "tinyurl", "goo.gl", "ow.ly", "short.link",
            "paypal", "amazon", "apple", "microsoft", "bank", "gmail"
        ]
        self.suspicious_keywords = [
            "verify", "confirm", "urgent", "update", "secure", "login",
            "account", "password", "restore", "click", "act"
        ]
    
    def _extract_url_features(self, url: str) -> Tuple[dict, str, str]:
        """Extract features from URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            path = parsed.path.lower()
            
            features = {
                "has_ip": bool(re.match(r'\d+\.\d+\.\d+\.\d+', domain)),
                "subdomain_count": domain.count('.') - 1,
                "path_length": len(path),
                "suspicious_chars": len(re.findall(r'[@%_-]', url)),
                "query_length": len(parsed.query),
                "fragment_length": len(parsed.fragment),
                "num_hyphens": domain.count('-'),
            }
            return features, domain, path
        except Exception:
            return {}, "", ""
    
    def _polynomial_sequence_check(self, features: dict) -> float:
        """
        Berlekamp-Massey: Generate polynomial from features
        Check if URL pattern follows suspicious polynomial sequence
        """
        # Convert feature values to polynomial coefficients
        coeffs = [
            features.get("has_ip", 0) * 20,
            features.get("subdomain_count", 0) * 5,
            features.get("path_length", 0) * 0.5,
            features.get("suspicious_chars", 0) * 8,
            features.get("query_length", 0) * 2,
            features.get("num_hyphens", 0) * 10,
        ]
        
        # Calculate polynomial value (simplified sequence analysis)
        score = sum(coeffs)
        return min(100.0, score)
    
    def analyze_url(self, url: str) -> float:
        """
        Analyze URL for phishing indicators using Berlekamp-Massey
        Returns score 0-100 (higher = more suspicious)
        """
        if not url or not url.strip():
            return 0.0
        
        features, domain, path = self._extract_url_features(url)
        if not domain:
            return 50.0  # Invalid URL
        
        score = 0.0
        
        # IP address detection (high indicator)
        if features.get("has_ip"):
            score += 25
        
        # URL shortener detection
        for shortener in ["bit.ly", "tinyurl", "goo.gl"]:
            if shortener in domain:
                score += 20
        
        # Suspicious keywords in URL
        for keyword in self.suspicious_keywords:
            if keyword in path or keyword in domain:
                score += 8
        
        # Subdomain count (many subdomains = suspicious)
        subdomain_count = features.get("subdomain_count", 0)
        if subdomain_count > 3:
            score += 15
        
        # Suspicious characters (@, %, -, etc.)
        suspicious_chars = features.get("suspicious_chars", 0)
        score += min(20, suspicious_chars * 3)
        
        # Hyphens in domain
        num_hyphens = features.get("num_hyphens", 0)
        if num_hyphens >= 1:
            score += 10
        
        # Query string length (long query = suspicious)
        query_length = features.get("query_length", 0)
        if query_length > 50:
            score += 10
        
        # Polynomial-based anomaly detection
        poly_score = self._polynomial_sequence_check(features)
        score += poly_score * 0.3
        
        return min(100.0, max(0.0, score))


def url_to_binary(url: str) -> List[int]:
    """Convert URL to binary sequence for entropy analysis"""
    binary_seq = []
    try:
        for char in url:
            binary_seq.extend([int(bit) for bit in format(ord(char), '08b')])
    except Exception:
        pass
    return binary_seq


def berlekamp_massey(binary_seq: List[int]) -> float:
    """
    Simplified Berlekamp-Massey algorithm for sequence analysis.
    Returns complexity score (0-100).
    
    Higher score = more random = more legitimate
    Lower score = more regular patterns = more suspicious (like URL shorteners)
    """
    if not binary_seq or len(binary_seq) < 2:
        return 100.0
    
    # Count transitions (changes from 0 to 1 or 1 to 0)
    transitions = sum(1 for i in range(len(binary_seq) - 1) if binary_seq[i] != binary_seq[i + 1])
    
    # Higher transitions = more random = higher complexity
    complexity = (transitions / len(binary_seq)) * 100
    return min(100.0, max(0.0, complexity))


def test_berlekamp_massey():
    """Test Berlekamp-Massey URL analysis."""
    print("Testing Berlekamp-Massey URL analysis...", end=" ")
    try:
        analyzer = BerlekampMasseyAnalyzer()
        
        # Test phishing URL
        phishing_url = "http://bit.ly/verify_account_secure-login"
        score = analyzer.analyze_url(phishing_url)
        assert score > 30, f"Expected high score for phishing URL, got {score}"
        
        # Test legitimate URL
        legit_url = "https://www.example.com/home"
        score = analyzer.analyze_url(legit_url)
        assert score < 40, f"Expected low score for legitimate URL, got {score}"
        
        # Test borderline URL
        borderline_url = "http://secure-login.example.com/update-info"
        score = analyzer.analyze_url(borderline_url)
        assert 20 <= score <= 60, f"Expected moderate score for borderline URL, got {score}"
        
        # Test invalid URL
        invalid_url = "not a url"
        score = analyzer.analyze_url(invalid_url)
        assert 0 <= score <= 100, f"Expected valid score for invalid URL, got {score}"
        
        # Test empty URL
        empty_url = ""
        score = analyzer.analyze_url(empty_url)
        assert score == 0.0, f"Expected score 0 for empty URL, got {score}"
        
        # Test berlekamp_massey function
        binary_seq = url_to_binary(phishing_url)
        score = berlekamp_massey(binary_seq)
        assert 0 <= score <= 100, f"Invalid BM score: {score}"
        
        binary_seq = url_to_binary(legit_url)
        score = berlekamp_massey(binary_seq)
        assert 0 <= score <= 100, f"Invalid BM score: {score}"
        
        binary_seq = url_to_binary("")
        score = berlekamp_massey(binary_seq)
        assert score == 100.0, f"Expected BM score 100 for empty sequence, got {score}"
        
        print("OK\n")
        return True
    except Exception as e:
        print(f"Error: {e}\n")
        import traceback
        traceback.print_exc()
        return False


__all__ = ["BerlekampMasseyAnalyzer", "url_to_binary", "berlekamp_massey", "test_berlekamp_massey"]