"""
NLP and clustering services.
- BERT sentiment (positive/negative) – replace with trained BERT for production.
- Multi-label classification (sigmoid) – delay, overcrowding, cleanliness, staff, safety, infrastructure.
- Demo fallback – replace with trained BERT when weights are available.
"""
import re
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from ml.dbscan_cluster import run_dbscan_on_records as _dbscan_records

# BERT models (lazy-loaded). Demo fallback used if import or load fails.
_sentiment_model = None
_sentiment_tokenizer = None
_multilabel_model = None
_multilabel_tokenizer = None
_multilabel_labels = [
    "delay", "overcrowding", "cleanliness", "staff", "safety", "infrastructure"
]
_bert_available = None


def clean_text(text: str) -> str:
    """Preprocess: lowercase, remove non-alpha (except spaces)."""
    if not text:
        return ""
    return re.sub(r"[^a-zA-Z\s]", "", text.lower()).strip()


# Demo fallback – replace with trained BERT for viva/production.
def _demo_fallback_sentiment(text: str) -> str:
    """Rule-based sentiment when BERT is not loaded. Demo fallback – replace with trained BERT."""
    t = clean_text(text)
    neg = ["late", "bad", "dirty", "rude", "unsafe", "crowded", "broken", "poor", "never", "worst", "terrible"]
    if any(w in t for w in neg):
        return "negative"
    return "positive"


# Demo fallback – replace with trained BERT multi-label for viva/production.
def _demo_fallback_issues(text: str) -> list:
    """Keyword-based issue detection when BERT not loaded. Demo fallback – replace with trained BERT."""
    t = clean_text(text)
    found = []
    if any(w in t for w in ["late", "delay", "wait", "slow"]):
        found.append("delay")
    if any(w in t for w in ["crowd", "packed", "overcrowd", "full"]):
        found.append("overcrowding")
    if any(w in t for w in ["dirty", "clean", "hygiene", "smell", "garbage"]):
        found.append("cleanliness")
    if any(w in t for w in ["staff", "driver", "conductor", "rude", "behavior"]):
        found.append("staff")
    if any(w in t for w in ["safe", "unsafe", "security", "danger"]):
        found.append("safety")
    if any(w in t for w in ["seat", "broken", "bus", "stop", "route", "infrastructure"]):
        found.append("infrastructure")
    return found if found else ["infrastructure"]


def _get_sentiment_models():
    """Load BERT for sentiment (binary). Used by predict_sentiment when BERT available."""
    global _sentiment_model, _sentiment_tokenizer, _bert_available
    if _bert_available is False:
        return None, None
    if _sentiment_model is None:
        try:
            from transformers import BertTokenizer, BertForSequenceClassification
            _sentiment_tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
            _sentiment_model = BertForSequenceClassification.from_pretrained(
                "bert-base-uncased", num_labels=2
            )
            _sentiment_model.eval()
            _bert_available = True
        except Exception:
            _bert_available = False
            return None, None
    return _sentiment_tokenizer, _sentiment_model


def _get_multilabel_models():
    """Load BERT for multi-label classification (sigmoid). Used by predict_issues when BERT available."""
    global _multilabel_model, _multilabel_tokenizer, _multilabel_labels
    if _bert_available is False:
        return None, None, _multilabel_labels
    if _multilabel_model is None:
        try:
            from transformers import BertTokenizer, BertForSequenceClassification
            _multilabel_tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
            _multilabel_model = BertForSequenceClassification.from_pretrained(
                "bert-base-uncased", num_labels=len(_multilabel_labels)
            )
            _multilabel_model.eval()
        except Exception:
            _bert_available = False
            return None, None, _multilabel_labels
    return _multilabel_tokenizer, _multilabel_model, _multilabel_labels


def predict_sentiment(text: str) -> str:
    """
    Sentiment: positive or negative.
    Uses BERT when available; otherwise demo fallback – replace with trained BERT.
    """
    cleaned = clean_text(text) or text
    tok, model = _get_sentiment_models()
    if model is None:
        return _demo_fallback_sentiment(text)
    import torch
    with torch.no_grad():
        inputs = tok(cleaned, return_tensors="pt", truncation=True, padding=True, max_length=128)
        outputs = model(**inputs)
        pred = torch.argmax(outputs.logits, dim=1).item()
    return "positive" if pred == 1 else "negative"


def predict_issues(text: str) -> list:
    """
    Multi-label classification: delay, overcrowding, cleanliness, staff, safety, infrastructure.
    Uses BERT with sigmoid when available; otherwise demo fallback – replace with trained BERT.
    """
    cleaned = clean_text(text) or text
    tok, model, labels = _get_multilabel_models()
    if model is None:
        return _demo_fallback_issues(text)
    import torch
    with torch.no_grad():
        inputs = tok(cleaned, return_tensors="pt", truncation=True, padding=True, max_length=128)
        logits = model(**inputs).logits[0]
        probs = torch.sigmoid(logits)
    return [labels[i] for i, p in enumerate(probs) if p.item() > 0.5]


def run_dbscan_on_records(records):
    """DBSCAN clustering runs here: density-based spatial clustering on lat/lon (hotspots)."""
    return _dbscan_records(records)
