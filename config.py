from dataclasses import dataclass
from typing import List, Dict, Optional
from pathlib import Path


@dataclass
class ModelConfig:
    """Configurație pentru modulul NLP."""
    # TF-IDF Settings
    ngram_range: tuple = (1, 2)
    max_features: int = 20000
    stop_words: str = "english"
    min_df: int = 2
    max_df: float = 0.95
    
    # Random Forest Settings
    n_estimators: int = 100
    max_depth: int = 15
    random_state: int = 42
    n_jobs: int = -1
    
    def to_dict(self) -> Dict:
        """Convertește configurația în dicționar."""
        return {
            'ngram_range': self.ngram_range,
            'max_features': self.max_features,
            'stop_words': self.stop_words,
            'min_df': self.min_df,
            'max_df': self.max_df,
            'n_estimators': self.n_estimators,
            'max_depth': self.max_depth,
            'random_state': self.random_state,
        }


@dataclass
class ThresholdConfig:
    """Configurație pentru pragurile de decizie."""
    nlp_threshold: float = 0.6
    bm_threshold: float = 40.0
    
    # Thresholds optionale pentru scenarii specific
    high_security_nlp: float = 0.5  # Mod strict
    low_security_nlp: float = 0.7   # Mod permisiv
    high_security_bm: float = 35.0
    low_security_bm: float = 50.0


@dataclass
class DataConfig:
    """Configurație pentru cărări de date."""
    training_data_path: Path = Path("data/emails.csv")
    test_data_path: Path = Path("data/test_emails.csv")
    demo_data_path: Path = Path("data/demo_attack.csv")
    medical_data_path: Path = Path("data/emails_medical.csv")
    
    # Coloane așteptate
    text_column: str = "email_text"
    label_column: str = "label"
    
    # Validare
    min_samples: int = 100
    test_split: float = 0.2
    random_state: int = 42


@dataclass
class LoggingConfig:
    """Configurație pentru logging."""
    log_file: str = "phishing_detection.log"
    analysis_log_file: str = "analysis_log.jsonl"
    level: str = "INFO"
    format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    max_file_size: int = 10 * 1024 * 1024  # 10 MB
    backup_count: int = 5


@dataclass
class SystemConfig:
    """Configurație completă a sistemului."""
    model: Optional[ModelConfig] = None
    thresholds: Optional[ThresholdConfig] = None
    data: Optional[DataConfig] = None
    logging: Optional[LoggingConfig] = None
    
    # Feature flags
    enable_logging: bool = True
    enable_metrics: bool = True
    cache_model: bool = True
    
    def __post_init__(self):
        """Inițializează subcomponente dacă nu sunt setate."""
        if self.model is None:
            self.model = ModelConfig()
        if self.thresholds is None:
            self.thresholds = ThresholdConfig()
        if self.data is None:
            self.data = DataConfig()
        if self.logging is None:
            self.logging = LoggingConfig()


# Configurație Default
DEFAULT_CONFIG = SystemConfig()

# Configurații Predefinite pentru Disertație
HIGH_SECURITY_CONFIG = SystemConfig(
    model=ModelConfig(n_estimators=150, max_depth=20),
    thresholds=ThresholdConfig(nlp_threshold=0.5, bm_threshold=35.0)
)

BALANCED_CONFIG = SystemConfig(
    model=ModelConfig(n_estimators=100, max_depth=15),
    thresholds=ThresholdConfig(nlp_threshold=0.6, bm_threshold=40.0)
)

PERFORMANCE_CONFIG = SystemConfig(
    model=ModelConfig(n_estimators=50, max_depth=10),
    thresholds=ThresholdConfig(nlp_threshold=0.7, bm_threshold=50.0)
)


# Legacy support - pentru compatibilitate cu cod existent
NLP_THRESHOLD = DEFAULT_CONFIG.thresholds.nlp_threshold if DEFAULT_CONFIG.thresholds else 0.6
BM_THRESHOLD = DEFAULT_CONFIG.thresholds.bm_threshold if DEFAULT_CONFIG.thresholds else 40.0
