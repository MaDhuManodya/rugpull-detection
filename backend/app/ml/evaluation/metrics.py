"""
app/ml/evaluation/metrics.py
Standard evaluation metrics for binary classification.
"""
import numpy as np
try:
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
except ImportError:
    pass

class MetricsEvaluator:
    @staticmethod
    def evaluate(y_true: np.ndarray, y_prob: np.ndarray, threshold: float = 0.5) -> dict:
        y_pred = (y_prob >= threshold).astype(int)
        
        try:
            auc = roc_auc_score(y_true, y_prob)
        except ValueError:
            auc = 0.5 # Handle single-class batch edge cases during testing
            
        cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
        
        return {
            "accuracy": float(accuracy_score(y_true, y_pred)),
            "precision": float(precision_score(y_true, y_pred, zero_division=0)),
            "recall": float(recall_score(y_true, y_pred, zero_division=0)),
            "f1_score": float(f1_score(y_true, y_pred, zero_division=0)),
            "roc_auc": float(auc),
            "confusion_matrix": cm.tolist()
        }
