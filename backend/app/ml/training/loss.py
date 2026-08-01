"""
app/ml/training/loss.py
Weighted Binary Cross-Entropy Loss to handle class imbalance.
"""
import torch
import torch.nn as nn

class WeightedBCELoss(nn.Module):
    def __init__(self, pos_weight: float):
        super().__init__()
        # pos_weight = (num_neg_samples / num_pos_samples)
        self.criterion = nn.BCEWithLogitsLoss(pos_weight=torch.tensor([pos_weight]))
        
    def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        return self.criterion(logits, targets)
