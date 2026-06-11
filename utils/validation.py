"""
Modul de Utilități și Validare
================================

Furnizează funcții utile pentru validare, preprocessing,
și operații generale ale sistemului de detecție.
"""

import logging
import re
import json
from typing import List, Dict, Tuple, Optional, Union, Any
from pathlib import Path
from urllib.parse import urlparse
from datetime import datetime

logger = logging.getLogger(__name__)


class DataValidator:
    """Validează și procesează datele de intrare."""
    
    @staticmethod
    def validate_email_text(text: str, min_length: int = 5, max_length: int = 10000) -> Tuple[bool, str]:
        """
        Validează textul unui email.
        
        Args:
            text: Textul de validat
            min_length: Lungimea minimă
            max_length: Lungimea maximă
            
        Returns:
            Tuple: (valid, message)
        """
        if not text or not isinstance(text, str):
            return False, "Email text must be a non-empty string"
        
        text = text.strip()
        
        if len(text) < min_length:
            return False, f"Email text too short (min {min_length} characters)"
        
        if len(text) > max_length:
            return False, f"Email text too long (max {max_length} characters)"
        
        return True, "Valid"
    
    @staticmethod
    def validate_url(url: str) -> Tuple[bool, str]:
        """
        Validează un URL.
        
        Args:
            url: URL-ul de validat
            
        Returns:
            Tuple: (valid, message)
        """
        if not url or not isinstance(url, str):
            return False, "URL must be a non-empty string"
        
        url = url.strip()
        
        # Verifică pattern de URL
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(url):
            return False, "Invalid URL format"
        
        try:
            parsed = urlparse(url)
            if not parsed.netloc:
                return False, "URL missing domain"
        except Exception as e:
            return False, f"URL parsing error: {str(e)}"
        
        return True, "Valid"
    
    @staticmethod
    def validate_dataset(csv_path: Path, text_column: str = "email_text", 
                        label_column: str = "label", min_samples: int = 100) -> Tuple[bool, str]:
        """
        Validează un CSV dataset.
        
        Args:
            csv_path: Calea la fisier CSV
            text_column: Numele coloanei de text
            label_column: Numele coloanei de etichete
            min_samples: Numărul minim de sample-uri
            
        Returns:
            Tuple: (valid, message)
        """
        if not csv_path.exists():
            return False, f"File not found: {csv_path}"
        
        try:
            import pandas as pd
            data = pd.read_csv(csv_path)
            
            if text_column not in data.columns:
                return False, f"Missing column: {text_column}"
            
            if label_column not in data.columns:
                return False, f"Missing column: {label_column}"
            
            if len(data) < min_samples:
                return False, f"Too few samples: {len(data)} < {min_samples}"
            
            # Validează etichetele
            valid_labels = set(data[label_column].unique())
            if not valid_labels.issubset({0, 1}):
                return False, f"Invalid labels: {valid_labels}"
            
            logger.info(f"Dataset validated: {len(data)} samples")
            return True, f"Valid ({len(data)} samples)"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"


class TextPreprocessor:
    """Procesează și normalizează text."""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Curață textul de caractere speciale și whitespace.
        
        Args:
            text: Textul de curățat
            
        Returns:
            str: Textul curățat
        """
        # Convertire la minuscule
        text = text.lower()
        
        # Elimină HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Elimină URL-uri
        text = re.sub(r'http\S+|www\S+', '', text)
        
        # Elimină email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Elimină caractere speciale, păstrând doar spații și punctuație de bază
        text = re.sub(r'[^a-z0-9\s.!?\-]', '', text)
        
        # Normalizează whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    @staticmethod
    def extract_features(text: str) -> Dict[str, Union[int, float]]:
        """
        Extrage caracteristici din text.
        
        Args:
            text: Textul de analizat
            
        Returns:
            Dict cu caracteristici: lungime, nr cuvinte, nr URL-uri, etc.
        """
        features = {
            'length': len(text),
            'word_count': len(text.split()),
            'uppercase_ratio': sum(1 for c in text if c.isupper()) / max(1, len(text)),
            'digit_ratio': sum(1 for c in text if c.isdigit()) / max(1, len(text)),
            'special_char_ratio': sum(1 for c in text if not c.isalnum() and c != ' ') / max(1, len(text)),
            'url_count': len(re.findall(r'http\S+|www\S+', text)),
            'email_count': len(re.findall(r'\S+@\S+', text)),
            'urgent_keywords': sum(1 for word in ['urgent', 'verify', 'confirm', 'act now'] if word in text.lower()),
        }
        
        return features
    
    @staticmethod
    def tokenize(text: str) -> List[str]:
        """
        Tokenizează textul.
        
        Args:
            text: Textul de tokenizat
            
        Returns:
            Lista de tokeni
        """
        # Eliminare whitespace și convertire la minuscule
        text = text.strip().lower()
        
        # Tokenizare simplă pe spații și punctuație
        tokens = re.findall(r'\b\w+\b', text)
        
        return tokens


class ResultsProcessor:
    """Procesează și salvează rezultatele analizei."""
    
    @staticmethod
    def save_analysis_result(
        result: Dict,
        output_file: str = "analysis_results.jsonl"
    ) -> bool:
        """
        Salvează rezultatul analizei în format JSONL.
        
        Args:
            result: Dicționar cu rezultatul
            output_file: Fișierul de ieșire
            
        Returns:
            bool: Success status
        """
        try:
            result['timestamp'] = datetime.now().isoformat()
            
            with open(output_file, 'a') as f:
                f.write(json.dumps(result) + '\n')
            
            logger.info(f"Result saved to {output_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving result: {e}")
            return False
    
    @staticmethod
    def generate_report(
        results: List[Dict],
        report_file: str = "analysis_report.txt"
    ) -> bool:
        """
        Generează un raport din mai multe rezultate.
        
        Args:
            results: Lista de rezultate
            report_file: Fișierul raportului
            
        Returns:
            bool: Success status
        """
        try:
            with open(report_file, 'w') as f:
                f.write("=" * 80 + '\n')
                f.write("RAPORT ANALIZĂ PHISHING\n")
                f.write("=" * 80 + '\n\n')
                
                total = len(results)
                phishing = sum(1 for r in results if r.get('verdict') == 'PHISHING')
                legitimate = sum(1 for r in results if r.get('verdict') == 'LEGITIMATE')
                
                f.write(f"Total emails: {total}\n")
                f.write(f"Phishing: {phishing} ({phishing/total*100:.1f}%)\n")
                f.write(f"Legitimate: {legitimate} ({legitimate/total*100:.1f}%)\n\n")
                
                f.write("-" * 80 + '\n')
                f.write("DETALII\n")
                f.write("-" * 80 + '\n\n')
                
                for i, result in enumerate(results, 1):
                    f.write(f"{i}. {result.get('verdict')}\n")
                    f.write(f"   NLP Score: {result.get('nlp_score', 0):.3f}\n")
                    f.write(f"   BM Score: {result.get('bm_score', 0):.1f}\n")
                    f.write(f"   URL: {result.get('email_url', 'N/A')}\n\n")
            
            logger.info(f"Report saved to {report_file}")
            return True
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return False


class URLAnalyzer:
    """Analizează caracteristicile URL-urilor."""
    
    @staticmethod
    def extract_url_features(url: str) -> Dict[str, Any]:
        """
        Extrage caracteristici din URL.
        
        Args:
            url: URL-ul de analizat
            
        Returns:
            Dict cu caracteristici
        """
        try:
            parsed = urlparse(url)
            
            features = {
                'scheme': parsed.scheme,
                'domain': parsed.netloc,
                'path_length': len(parsed.path),
                'has_port': parsed.port is not None,
                'port': parsed.port,
                'param_count': len(parsed.params),
                'query_count': len(parsed.query.split('&')) if parsed.query else 0,
                'fragment_length': len(parsed.fragment),
                'is_ip': bool(re.match(r'^\d+\.\d+\.\d+\.\d+$', parsed.netloc)),
                'domain_length': len(parsed.netloc),
                'suspicious_chars': sum(1 for c in url if c in ['@', ':', '-']),
            }
            
            return features
        except Exception as e:
            logger.warning(f"Error extracting URL features: {e}")
            return {}
