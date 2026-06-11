import streamlit as st  # type: ignore
import pandas as pd
from pathlib import Path
import os
from typing import List, Tuple, Dict, Optional
import logging
from datetime import datetime
import json

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix
    _sklearn_available = True
except Exception:
    TfidfVectorizer = None
    RandomForestClassifier = None
    precision_score = None
    recall_score = None
    f1_score = None
    confusion_matrix = None
    _sklearn_available = False

from bm_module import BerlekampMasseyAnalyzer  # type: ignore

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('phishing_detection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

SUSPICIOUS_TOKENS = [
    "urgent", "verify", "click", "account", "password", "login", "bank",
    "update", "confirm", "security", "ssn", "social", "verify", "bit.ly",
    "tinyurl", "paypal", "invoice", "wire", "transfer"
]


class NLPDetector:
    """
    NLP-based Phishing Detector
    
    Uses TF-IDF Vectorization + Random Forest Classifier for classification.
    Falls back to token-matching mode if sklearn is unavailable.
    
    Attributes:
        vectorizer: TfidfVectorizer for text transformation
        clf: RandomForestClassifier for predictions
        _is_trained: Boolean indicating if model is trained
        _token_set: Set of tokens for ML-free detection
    """
    
    def __init__(self) -> None:
        """Initialize NLP detector with ML or fallback mode."""
        self._is_trained = False
        if _sklearn_available and TfidfVectorizer is not None and RandomForestClassifier is not None:
            self.vectorizer = TfidfVectorizer(
                ngram_range=(1, 2),
                max_features=20000,
                stop_words="english",
                min_df=2,
                max_df=0.95,
            )
            self.clf = RandomForestClassifier(n_estimators=100, max_depth=15, random_state=42)
            logger.info("NLP Detector initialized with scikit-learn")
        else:
            self._token_set: set = set(SUSPICIOUS_TOKENS)
            logger.warning("NLP Detector using fallback token-matching mode")

    def train(self, texts: List[str], labels: List[int]) -> None:
        """
        Train the model on training data.
        
        Args:
            texts: List of emails for training
            labels: List of labels (0=legitimate, 1=phishing)
        """
        if _sklearn_available:
            try:
                self.vectorizer.fit(texts)
                X = self.vectorizer.transform(texts)
                self.clf.fit(X, labels)
                self._is_trained = True
                logger.info(f"NLP model trained on {len(texts)} samples")
            except Exception as e:
                logger.error(f"Error training NLP model: {e}")
                self._is_trained = False
        else:
            phishing_tokens: Dict[str, int] = {}
            for text, label in zip(texts, labels):
                if label:
                    for tok in text.lower().split():
                        if len(tok) > 2:
                            phishing_tokens[tok] = phishing_tokens.get(tok, 0) + 1
            top = sorted(phishing_tokens.items(), key=lambda x: -x[1])[:50]
            for tok, _ in top:
                self._token_set.add(tok)
            logger.info(f"Token set updated with {len(self._token_set)} suspicious tokens")

    def predict(self, text: str) -> float:
        """
        Predict the probability that text is phishing.
        
        Args:
            text: Email text to analyze
            
        Returns:
            float: Score between 0.0 and 1.0, where 1.0 = definitely phishing
        """
        if _sklearn_available and self._is_trained:
            try:
                X = self.vectorizer.transform([text])
                proba = self.clf.predict_proba(X)[0][1]
                return float(proba)
            except Exception as e:
                logger.warning(f"Error in ML prediction: {e}, falling back to token matching")
        
        text_l = text.lower()
        tokens = text_l.split()
        if not tokens:
            return 0.0
        hits = sum(1 for t in tokens if any(st in t for st in self._token_set))
        score = hits / max(1, len(tokens))
        return min(1.0, score * 2.0)


def hybrid_decision(nlp_score: float, bm_score: float, nlp_thresh: float = 0.6, bm_thresh: float = 40) -> str:
    """
    Make final decision based on NLP and BM scores.
    
    Uses hybrid strategy: EMAIL IS PHISHING IF NLP score is high OR BM score is low.
    
    Args:
        nlp_score: NLP score (0.0-1.0), higher = more phishing
        bm_score: Berlekamp-Massey score (0-100), lower = more phishing (regular patterns)
        nlp_thresh: Threshold for NLP (default 0.6)
        bm_thresh: Threshold for BM (default 40)
        
    Returns:
        str: "PHISHING" or "LEGITIMATE"
    """
    # PHISHING if:
    # - NLP score is high (suspicious text) OR
    # - BM score is low (regular URL patterns, like shorteners)
    if nlp_score >= nlp_thresh or bm_score < bm_thresh:
        return "PHISHING"
    return "LEGITIMATE"


@st.cache_resource
def load_training_data() -> Optional[pd.DataFrame]:
    """
    Load training data from CSV.
    Result is cached for performance.
    
    Returns:
        DataFrame with columns: email_text, label
    """
    csv_path = Path("data/emails.csv")
    if not csv_path.exists():
        logger.error(f"Training data not found: {csv_path}")
        return None
    
    try:
        data = pd.read_csv(csv_path)
        if "email_text" not in data.columns or "label" not in data.columns:
            logger.error("CSV missing required columns: email_text, label")
            return None
        logger.info(f"Loaded {len(data)} training samples")
        return data
    except Exception as e:
        logger.error(f"Error loading training data: {e}")
        return None


@st.cache_resource
def get_trained_nlp_detector(data: pd.DataFrame) -> Optional[NLPDetector]:
    """
    Get trained NLP detector. Result is cached.
    
    Args:
        data: DataFrame with training data
        
    Returns:
        Trained NLPDetector or None on failure
    """
    if data is None:
        return None
    
    try:
        nlp = NLPDetector()
        nlp.train(data["email_text"].astype(str).tolist(), data["label"].tolist())
        return nlp
    except Exception as e:
        logger.error(f"Error initializing NLP detector: {e}")
        return None


def evaluate_model(nlp: NLPDetector, data: pd.DataFrame, threshold: float = 0.6) -> Dict[str, float]:
    """
    Evaluate NLP model performance on training data.
    
    Args:
        nlp: Trained NLP detector
        data: Evaluation data
        threshold: Classification threshold
        
    Returns:
        Dict with metrics: precision, recall, f1, accuracy
    """
    if not _sklearn_available or precision_score is None or recall_score is None or f1_score is None or confusion_matrix is None:
        logger.warning("sklearn not available, skipping evaluation metrics")
        return {}
    
    predictions = [nlp.predict(text) for text in data["email_text"].astype(str)]
    y_pred = [1 if p >= threshold else 0 for p in predictions]
    y_true = data["label"].tolist()
    
    try:
        metrics = {
            "accuracy": sum(1 for y1, y2 in zip(y_true, y_pred) if y1 == y2) / len(y_true),
            "precision": float(precision_score(y_true, y_pred, zero_division=0)),
            "recall": float(recall_score(y_true, y_pred, zero_division=0)),
            "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        }
        
        # Confusion Matrix
        cm = confusion_matrix(y_true, y_pred)
        tn, fp, fn, tp = int(cm[0, 0]), int(cm[0, 1]), int(cm[1, 0]), int(cm[1, 1])
        metrics["tn"], metrics["fp"], metrics["fn"], metrics["tp"] = tn, fp, fn, tp
        
        logger.info(f"Model evaluation - F1: {metrics['f1']:.3f}, Accuracy: {metrics['accuracy']:.3f}")
        return metrics
    except Exception as e:
        logger.error(f"Error evaluating model: {e}")
        return {}


def log_analysis_result(email_text: str, email_url: str, verdict: str, nlp_score: float, bm_score: float, timestamp: Optional[str] = None) -> None:
    """
    Log analysis result for auditing.
    
    Args:
        email_text: Analyzed email text
        email_url: URL from email
        verdict: Final decision
        nlp_score: NLP score
        bm_score: BM score
        timestamp: Analysis timestamp
    """
    if timestamp is None:
        timestamp = datetime.now().isoformat()
    
    result = {
        "timestamp": timestamp,
        "verdict": verdict,
        "nlp_score": nlp_score,
        "bm_score": bm_score,
        "email_url": email_url,
        "text_length": len(email_text)
    }
    
    try:
        # Save to results file
        with open("analysis_log.jsonl", "a") as f:
            f.write(json.dumps(result) + "\n")
        logger.info(f"Analysis logged: {verdict}")
    except Exception as e:
        logger.error(f"Error logging analysis: {e}")


# Initialize Streamlit
st.set_page_config(page_title="Phishing Detection - Hybrid System", layout="wide")
st.title("🔒 Hybrid Phishing Detection System")
st.markdown("**Machine Learning + Berlekamp-Massey Algorithm**")
st.markdown("---")

logger.info("=== Streamlit App Started ===")

# Load training data
training_data = load_training_data()
if training_data is None:
    st.error("❌ Training data could not be loaded. Check data/emails.csv")
    st.stop()

# Get trained model
nlp_detector = get_trained_nlp_detector(training_data)  # type: ignore
if nlp_detector is None:
    st.error("❌ NLP detector could not be initialized.")
    st.stop()

# Sidebar Configuration
st.sidebar.header("⚙️ System Configuration")
nlp_threshold = st.sidebar.slider("NLP Threshold (classification threshold)", 0.0, 1.0, 0.6, step=0.05)
bm_threshold = st.sidebar.slider("BM Threshold (Berlekamp-Massey threshold)", 0, 100, 40, step=5)

st.sidebar.markdown("---")
st.sidebar.subheader("📈 Model Performance")

# Evaluate and show metrics
try:
    metrics = evaluate_model(nlp_detector, training_data, nlp_threshold)  # type: ignore
    if metrics:
        col1, col2, col3, col4 = st.sidebar.columns(4)
        with col1:
            st.sidebar.metric("Accuracy", f"{metrics.get('accuracy', 0):.2%}")
        with col2:
            st.sidebar.metric("Precision", f"{metrics.get('precision', 0):.2%}")
        with col3:
            st.sidebar.metric("Recall", f"{metrics.get('recall', 0):.2%}")
        with col4:
            st.sidebar.metric("F1 Score", f"{metrics.get('f1', 0):.2%}")
        
        # Confusion Matrix
        if metrics.get('tp') is not None:
            st.sidebar.write("**Confusion Matrix:**")
            cm_data = pd.DataFrame(
                [[int(metrics.get('tp', 0)), int(metrics.get('fp', 0))],
                 [int(metrics.get('fn', 0)), int(metrics.get('tn', 0))]],
                columns=["Predicted Phishing", "Predicted Legitimate"],
                index=["Actual Phishing", "Actual Legitimate"]
            )
            st.sidebar.dataframe(cm_data)
except Exception as e:
    logger.error(f"Error displaying metrics: {e}")

st.sidebar.markdown("---")
st.sidebar.info("💡 Adjust thresholds to fine-tune detection sensitivity")

# Input Section
st.subheader("📧 Analyze an Email")
col1, col2 = st.columns(2)

with col1:
    email_text = st.text_area(
        "Email text:",
        height=120,
        placeholder="Enter email text to analyze..."
    )

with col2:
    email_url = st.text_input(
        "URL from email:",
        placeholder="https://example.com"
    )


# Analyze Button
if st.button("🔍 Analyze Email", use_container_width=True):
    timestamp = datetime.now().isoformat()
    
    if email_text.strip() and email_url.strip():
        with st.spinner("⏳ Analyzing..."):
            try:
                # Get NLP score
                nlp_score = nlp_detector.predict(email_text)  # type: ignore
                
                # Get BM score
                bm_analyzer = BerlekampMasseyAnalyzer()
                bm_score = bm_analyzer.analyze_url(email_url)
                
                # Get verdict
                verdict = hybrid_decision(nlp_score, bm_score, nlp_threshold, bm_threshold)
                
                # Log the analysis
                log_analysis_result(email_text, email_url, verdict, nlp_score, bm_score, timestamp)
                
                # Display results
                st.markdown("---")
                st.subheader("📊 Analysis Results")
                
                metric1, metric2, metric3 = st.columns(3)
                
                with metric1:
                    st.metric("📝 NLP Score", f"{nlp_score:.3f}", f"{nlp_score*100:.1f}%")
                
                with metric2:
                    st.metric("🔗 BM Score", f"{bm_score:.1f}", f"{bm_score:.0f}%")
                
                with metric3:
                    if verdict == "PHISHING":
                        st.error(f"⚠️ {verdict}")
                    else:
                        st.success(f"✅ {verdict}")
                
                # Detailed Analysis
                st.markdown("---")
                st.subheader("🔬 Detailed Analysis")
                
                tab1, tab2, tab3 = st.tabs(["Text Analysis", "URL Analysis", "Final Decision"])
                
                with tab1:
                    st.write(f"**NLP Score:** {nlp_score:.3f}")
                    st.write(f"**NLP Threshold (configured):** {nlp_threshold:.2f}")
                    
                    if nlp_score >= nlp_threshold:
                        st.warning(f"⚠️ Email contains phishing indicators (score: {nlp_score:.3f})")
                    else:
                        st.info(f"✓ Email appears legitimate from NLP perspective (score: {nlp_score:.3f})")
                    
                    st.write("**Explanation:** NLP module uses TF-IDF + Random Forest to detect typical phishing characteristics.")
                
                with tab2:
                    st.write(f"**Analyzed URL:** `{email_url}`")
                    st.write(f"**Berlekamp-Massey Score:** {bm_score:.1f}")
                    st.write(f"**BM Threshold (configured):** {bm_threshold}")
                    
                    if bm_score >= bm_threshold:
                        st.warning(f"⚠️ URL has suspicious indicators (score: {bm_score:.1f})")
                    else:
                        st.info(f"✓ URL appears legitimate (score: {bm_score:.1f})")
                    
                    st.write("**Explanation:** Berlekamp-Massey algorithm analyzes entropy and cryptographic structure of URL.")
                
                with tab3:
                    st.write(f"**Final Verdict: {verdict}**")
                    st.write(f"**Timestamp:** {timestamp}")
                    st.write(f"**Decision Reason:** NLP={nlp_score:.3f} (threshold {nlp_threshold}) | BM={bm_score:.1f} (threshold {bm_threshold})")
                    
                    # Decision logic explanation
                    if verdict == "PHISHING":
                        if nlp_score >= nlp_threshold and bm_score >= bm_threshold:
                            st.write("✓ Both indicators suggest **PHISHING**")
                        elif nlp_score >= nlp_threshold:
                            st.write("✓ **NLP** indicator suggests phishing")
                        else:
                            st.write("✓ **Berlekamp-Massey** indicator suggests phishing")
                    else:
                        st.write("✓ Both indicators suggest **LEGITIMATE EMAIL**")
                
                # Download analysis report
                st.markdown("---")
                st.subheader("📥 Download Report")
                
                report = f"""
PHISHING ANALYSIS REPORT
========================
Timestamp: {timestamp}
Verdict: {verdict}

SCORES:
- NLP Score: {nlp_score:.3f} (Threshold: {nlp_threshold})
- BM Score: {bm_score:.1f} (Threshold: {bm_threshold})

ANALYZED URL:
{email_url}

EMAIL TEXT (first 500 characters):
{email_text[:500]}...

CONCLUSION:
{verdict}
"""
                
                st.download_button(
                    label="📄 Download Report TXT",
                    data=report,
                    file_name=f"phishing_analysis_{timestamp.replace(':', '-')}.txt",
                    mime="text/plain"
                )
                
            except Exception as e:
                logger.error(f"Error during analysis: {e}", exc_info=True)
                st.error(f"❌ Error: {str(e)}")
                st.error(f"Details: {type(e).__name__}")
    else:
        st.warning("⚠️ Complete both fields (email and URL)!")

st.markdown("---")
st.info("🤖 **Hybrid System** based on Machine Learning + Berlekamp-Massey Algorithm\nFor more information, consult documentation in `docs/` folder")


# Sample CSV content for reference
sample_csv = """email_text,label
"Click here to verify your PayPal account immediately",1
"Your account needs urgent verification",1
"Update your banking information now",1
"Confirm your Amazon password for security",1
"Act now to restore your account access",1
"Dear Sir/Madam verify your account details",1
"URGENT: Click link to verify identity",1
"Secure your account - click here",1
"Hello John. Meeting tomorrow at 2pm?",0
"The project deadline is next Friday",0
"Thank you for your purchase",0
"Team lunch scheduled for noon",0
"Project update: completed on schedule",0
"Please review the attached document",0
"Monthly report is ready for review",0
"Confirmed: Conference call at 3pm",0
"Invoice #12345 has been sent",0
"Your order has been shipped",0
"""

# Footer
st.markdown("---")
st.markdown("""
**Academic References:**
- TF-IDF: Sparse, High-Dimensional Vector Space Model for NLP
- Random Forest: Ensemble Learning for Classification
- Berlekamp-Massey Algorithm: Linear Complexity Sequence Analysis
- Phishing Detection: [APWG - Anti-Phishing Working Group](https://apwg.org/)

**Author:** Hybrid Phishing Detection System
**Version:** 1.0.0
**Date:** 2026-01-14
""")
