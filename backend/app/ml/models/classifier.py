"""
app/ml/models/classifier.py
Binary Classification Head (MLP).
"""
import torch
import torch.nn as nn

class BinaryClassificationHead(nn.Module):
    def __init__(self, in_channels: int, hidden_channels: int = 64):
        super().__init__()
        self.mlp = nn.Sequential(
            nn.Linear(in_channels, hidden_channels),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(hidden_channels, 1)
        )

    def forward(self, embeddings: torch.Tensor) -> torch.Tensor:
        """
        Outputs pre-sigmoid logits.
        """
        return self.mlp(embeddings)
        
    def predict_proba(self, embeddings: torch.Tensor) -> torch.Tensor:
        """
        Outputs probabilities in [0, 1].
        """
        logits = self.forward(embeddings)
        return torch.sigmoid(logits)
