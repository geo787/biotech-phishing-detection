import sys
import os
from pathlib import Path

# Add project root to path only at the end, not at the beginning
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

def test_imports():
    """Test main imports."""
    print("Checking imports...", end=" ")
    try:
        print("config...", end=" ")
        from config import DEFAULT_CONFIG, HIGH_SECURITY_CONFIG
        
        print("app...", end=" ")
        from app import NLPDetector, hybrid_decision, load_training_data # type: ignore
        
        print("evaluation_module...", end=" ")
        from evaluation_module import calculate_metrics, ModelMetrics
        
        print("utils.validation...", end=" ")
        from utils.validation import DataValidator, TextPreprocessor
        
        print("bm_module...", end=" ")
        from bm_module import BerlekampMasseyAnalyzer
        
        print("OK\n")
        return True
    except Exception as e:
        print(f"\nImport Error: {e}\n")
        return False


def test_validation():
    """Test validation module."""
    print("Testing validation...", end=" ")
    try:
        from utils.validation import DataValidator
        
        # Test email validation
        valid, msg = DataValidator.validate_email_text("Test email text")
        assert valid, "Email validation failed"
        
        # Test URL validation
        valid, msg = DataValidator.validate_url("https://example.com")
        assert valid, "URL validation failed"
        
        print("OK\n")
        return True
    except Exception as e:
        print(f"Error: {e}\n")
        return False


def test_nlp_detector():
    """Test NLP detector."""
    print("Testing NLP Detector...", end=" ")
    try:
        from app import NLPDetector # type: ignore
        
        nlp = NLPDetector()
        
        # Test train
        texts = ["Click here", "Meeting tomorrow", "Verify account"]
        labels = [1, 0, 1]
        nlp.train(texts, labels)
        
        # Test predict
        score = nlp.predict("Click here to verify")
        assert 0 <= score <= 1, f"Invalid score: {score}"
        
        print("OK\n")
        return True
    except Exception as e:
        print(f"Error: {e}\n")
        return False


def test_metrics():
    """Test metrics calculation."""
    print("Testing metrics calculation...", end=" ")
    try:
        from evaluation_module import calculate_metrics
        
        y_true = [0, 1, 1, 0, 1, 0]
        y_pred = [0, 1, 0, 0, 1, 1]
        
        metrics = calculate_metrics(y_true, y_pred)
        
        # Verify metrics are reasonable
        assert 0 <= metrics.accuracy <= 1, "Invalid accuracy"
        assert 0 <= metrics.precision <= 1, "Invalid precision"
        assert 0 <= metrics.recall <= 1, "Invalid recall"
        assert 0 <= metrics.f1 <= 1, "Invalid f1"
        
        print("OK\n")
        return True
    except Exception as e:
        print(f"Error: {e}\n")
        return False


def test_hybrid_decision():
    """Test hybrid decision function."""
    print("Testing hybrid decision...", end=" ")
    try:
        from app import hybrid_decision # type: ignore
        
        # Test phishing detection
        verdict1 = hybrid_decision(0.8, 45.0)
        assert verdict1 == "PHISHING", f"Expected PHISHING, got {verdict1}"
        
        # Test legitimate detection
        verdict2 = hybrid_decision(0.3, 20.0)
        assert verdict2 == "LEGITIMATE", f"Expected LEGITIMATE, got {verdict2}"
        
        # Test threshold boundary
        verdict3 = hybrid_decision(0.6, 40.0)
        assert verdict3 == "PHISHING", "Threshold should trigger"
        
        print("OK\n")
        return True
    except Exception as e:
        print(f"Error: {e}\n")
        return False


def test_config():
    """Test configuration system."""
    print("Testing configurations...", end=" ")
    try:
        from config import (
            DEFAULT_CONFIG,
            HIGH_SECURITY_CONFIG,
            BALANCED_CONFIG,
            PERFORMANCE_CONFIG
        )
        
        # Verify all configs are valid
        assert DEFAULT_CONFIG.model is not None, "Default config missing model"
        assert HIGH_SECURITY_CONFIG.thresholds is not None, "HIGH_SECURITY_CONFIG missing thresholds"
        assert BALANCED_CONFIG.thresholds is not None, "BALANCED_CONFIG missing thresholds"
        assert HIGH_SECURITY_CONFIG.thresholds.nlp_threshold < BALANCED_CONFIG.thresholds.nlp_threshold
        
        print("OK\n")
        return True
    except Exception as e:
        print(f"Error: {e}\n")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("PHISHING DETECTION SYSTEM - COMPLETE VERIFICATION")
    print("=" * 60)
    print()
    
    tests = [
        ("Imports", test_imports),
        ("Validation", test_validation),
        ("NLP Detector", test_nlp_detector),
        ("Metrics", test_metrics),
        ("Hybrid Decision", test_hybrid_decision),
        ("Configurations", test_config),
    ]
    
    results = []
    for name, test_func in tests:
        result = test_func()
        results.append((name, result))
    
    # Summary
    print("=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{status} - {name}")
    
    print()
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\nSYSTEM IS COMPLETE AND FUNCTIONAL!")
        print("Ready for dissertation!\n")
        return 0
    else:
        print("\nSome tests did not pass. Check errors above.\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
