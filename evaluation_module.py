from typing import Dict, List, Tuple, Optional, Union
import logging
from dataclasses import dataclass

try:
    from sklearn.metrics import (
        precision_score, recall_score, f1_score, accuracy_score,
        roc_auc_score, confusion_matrix, roc_curve, auc, classification_report,
        matthews_corrcoef, cohen_kappa_score
    )
    _sklearn_available = True
except ImportError:
    _sklearn_available = False
    precision_score = None  # type: ignore
    recall_score = None  # type: ignore
    f1_score = None  # type: ignore
    accuracy_score = None  # type: ignore
    roc_auc_score = None  # type: ignore
    confusion_matrix = None  # type: ignore
    roc_curve = None  # type: ignore
    auc = None  # type: ignore
    classification_report = None  # type: ignore
    matthews_corrcoef = None  # type: ignore
    cohen_kappa_score = None  # type: ignore

logger = logging.getLogger(__name__)


@dataclass
class ModelMetrics:
    """Container pentru metrici de model."""
    accuracy: float
    precision: float
    recall: float
    f1: float
    specificity: float
    false_positive_rate: float
    false_negative_rate: float
    mcc: Optional[float] = None  # Matthews Correlation Coefficient
    kappa: Optional[float] = None  # Cohen's Kappa
    auc_roc: Optional[float] = None  # AUC-ROC
    tp: int = 0  # True Positives
    fp: int = 0  # False Positives
    fn: int = 0  # False Negatives
    tn: int = 0  # True Negatives
    
    def to_dict(self) -> Dict[str, Union[float, None]]:
        """Convertește metricile în dicționar."""
        return {
            'accuracy': self.accuracy,
            'precision': self.precision,
            'recall': self.recall,
            'f1': self.f1,
            'specificity': self.specificity,
            'false_positive_rate': self.false_positive_rate,
            'false_negative_rate': self.false_negative_rate,
            'mcc': self.mcc,
            'kappa': self.kappa,
            'auc_roc': self.auc_roc,
        }
    
    def __str__(self) -> str:
        """Reprezentare string formatată."""
        return f"""
ModelMetrics:
- Accuracy: {self.accuracy:.3f}
- Precision: {self.precision:.3f}
- Recall: {self.recall:.3f}
- F1-Score: {self.f1:.3f}
- Specificity: {self.specificity:.3f}
- False Positive Rate: {self.false_positive_rate:.3f}
- False Negative Rate: {self.false_negative_rate:.3f}
- Matthews CC: {self.mcc}
- Cohen's Kappa: {self.kappa}
- AUC-ROC: {self.auc_roc}
        """


def calculate_metrics(
    y_true: List[int],
    y_pred: List[int],
    y_pred_proba: Optional[List[float]] = None
) -> ModelMetrics:
    """
    Calculează metrici comprehensive pentru modelul de clasificare.
    
    Args:
        y_true: Etichete reale (0/1)
        y_pred: Predicții binare (0/1)
        y_pred_proba: Probabilități pentru AUC-ROC (opțional)
        
    Returns:
        ModelMetrics: Container cu toate metricile calculate
        
    Raises:
        ValueError: Dacă lungimile sunt diferite sau sklearn nu e disponibil
    """
    if not _sklearn_available:
        logger.error("scikit-learn is required for metrics calculation")
        raise ImportError("scikit-learn is not available")
    
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred must have same length")
    
    if len(y_true) == 0:
        raise ValueError("Empty input arrays")
    
    # Import sklearn functions here to use them
    from sklearn.metrics import (
        confusion_matrix as cm_func,
        accuracy_score as acc_func,
        precision_score as prec_func,
        recall_score as rec_func,
        f1_score as f1_func,
        matthews_corrcoef as mcc_func,
        cohen_kappa_score as kappa_func,
        roc_auc_score as auc_func
    )
    
    # Confusion matrix
    cm = cm_func(y_true, y_pred)
    tn, fp, fn, tp = int(cm[0, 0]), int(cm[0, 1]), int(cm[1, 0]), int(cm[1, 1])
    
    # Basic metrics
    accuracy = float(acc_func(y_true, y_pred))
    precision = float(prec_func(y_true, y_pred, zero_division=0))
    recall = float(rec_func(y_true, y_pred, zero_division=0))
    f1 = float(f1_func(y_true, y_pred, zero_division=0))
    
    # Additional metrics
    specificity = float(tn / (tn + fp) if (tn + fp) > 0 else 0)
    false_positive_rate = float(fp / (fp + tn) if (fp + tn) > 0 else 0)
    false_negative_rate = float(fn / (fn + tp) if (fn + tp) > 0 else 0)
    
    # Advanced metrics
    mcc_val: Optional[float] = None
    try:
        mcc_val = float(mcc_func(y_true, y_pred))
    except:
        mcc_val = None
    
    kappa_val: Optional[float] = None
    try:
        kappa_val = float(kappa_func(y_true, y_pred))
    except:
        kappa_val = None
    
    auc_roc_val: Optional[float] = None
    if y_pred_proba is not None:
        try:
            auc_roc_val = float(auc_func(y_true, y_pred_proba))
        except:
            auc_roc_val = None
    
    logger.info(f"Metrics calculated - Accuracy: {accuracy:.3f}, F1: {f1:.3f}")
    
    return ModelMetrics(
        accuracy=accuracy,
        precision=precision,
        recall=recall,
        f1=f1,
        specificity=specificity,
        false_positive_rate=false_positive_rate,
        false_negative_rate=false_negative_rate,
        mcc=mcc_val,
        kappa=kappa_val,
        auc_roc=auc_roc_val,
        tp=tp,
        fp=fp,
        fn=fn,
        tn=tn
    )


def get_classification_report(y_true: List[int], y_pred: List[int]) -> str:
    """
    Generează raport detaliat de clasificare.
    
    Args:
        y_true: Etichete reale
        y_pred: Predicții
        
    Returns:
        str: Raport formatat
    """
    if not _sklearn_available:
        logger.error("scikit-learn is required")
        raise ImportError("scikit-learn is not available")
    
    from sklearn.metrics import classification_report as clf_report
    report = clf_report(
        y_true, y_pred,
        target_names=['Legitimate', 'Phishing']
    )
    return str(report)


def analyze_threshold_impact(
    y_true: List[int],
    y_proba: List[float],
    thresholds: Optional[List[float]] = None
) -> Dict[float, ModelMetrics]:
    """
    Analizează impactul diferitelor praguri asupra metricilor.
    
    Args:
        y_true: Etichete reale
        y_proba: Probabilități pentru clase pozitive
        thresholds: Lista de praguri de testat (default: 0.1-0.9)
        
    Returns:
        Dict: {threshold: ModelMetrics} pentru fiecare prag
    """
    if thresholds is None:
        thresholds = [round(x * 0.1, 1) for x in range(1, 10)]
    
    results = {}
    for threshold in thresholds:
        y_pred = [1 if p >= threshold else 0 for p in y_proba]
        try:
            metrics = calculate_metrics(y_true, y_pred, y_proba)
            results[threshold] = metrics
            logger.info(f"Threshold {threshold}: F1={metrics.f1:.3f}")
        except Exception as e:
            logger.error(f"Error calculating metrics for threshold {threshold}: {e}")
    
    return results


def find_optimal_threshold(
    y_true: List[int],
    y_proba: List[float],
    metric: str = 'f1'
) -> Tuple[float, ModelMetrics]:
    """
    Găsește pragul optim bazat pe o metrică specifică.
    
    Args:
        y_true: Etichete reale
        y_proba: Probabilități
        metric: Metrica de optimizat ('f1', 'accuracy', 'mcc', 'kappa')
        
    Returns:
        Tuple: (optimal_threshold, metrics_at_threshold)
    """
    threshold_results = analyze_threshold_impact(y_true, y_proba)
    
    if not threshold_results:
        raise ValueError("No thresholds analyzed successfully")
    
    # Găsește pragul cu cea mai bună metrică
    best_threshold = max(
        threshold_results.items(),
        key=lambda x: getattr(x[1], metric, 0)
    )
    
    logger.info(f"Optimal threshold for {metric}: {best_threshold[0]} with {metric}={getattr(best_threshold[1], metric):.3f}")
    
    return best_threshold[0], best_threshold[1]


def compare_models(
    models_predictions: Dict[str, Tuple[List[int], List[int]]]
) -> Dict[str, ModelMetrics]:
    """
    Compară performanța mai multor modele.
    
    Args:
        models_predictions: {model_name: (y_true, y_pred)}
        
    Returns:
        Dict: {model_name: ModelMetrics}
    """
    results = {}
    
    for model_name, (y_true, y_pred) in models_predictions.items():
        try:
            metrics = calculate_metrics(y_true, y_pred)
            results[model_name] = metrics
            logger.info(f"Model '{model_name}' - F1: {metrics.f1:.3f}, Accuracy: {metrics.accuracy:.3f}")
        except Exception as e:
            logger.error(f"Error evaluating model '{model_name}': {e}")
    
    return results
