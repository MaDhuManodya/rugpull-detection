import os

directories = [
    "app/ml",
    "app/ml/models",
    "app/ml/training",
    "app/ml/evaluation",
    "app/ml/inference",
    "app/ml/dataloaders"
]
for d in directories:
    os.makedirs(d, exist_ok=True)

# 1. Models: GATv2
with open("app/ml/models/gatv2.py", "w") as f:
    f.write('''"""
app/ml/models/gatv2.py
Graph Attention Network v2 Module.
Implements dynamic spatial attention as defined in Chapter 3.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F

try:
    from torch_geometric.nn import GATv2Conv
except ImportError:
    pass

class GATv2SpatialEncoder(nn.Module):
    def __init__(
        self, 
        in_channels: int = 22, 
        hidden_channels: int = 128, 
        out_channels: int = 128, 
        heads: int = 4, 
        num_layers: int = 2,
        dropout: float = 0.6
    ):
        super().__init__()
        self.num_layers = num_layers
        self.dropout = dropout
        
        self.convs = nn.ModuleList()
        
        # Input Layer
        self.convs.append(
            GATv2Conv(in_channels, hidden_channels, heads=heads, concat=True, dropout=dropout)
        )
        
        # Hidden Layers
        for _ in range(num_layers - 2):
            self.convs.append(
                GATv2Conv(hidden_channels * heads, hidden_channels, heads=heads, concat=True, dropout=dropout)
            )
            
        # Output Layer (Aggregate heads by averaging, concat=False)
        self.convs.append(
            GATv2Conv(hidden_channels * heads, out_channels, heads=1, concat=False, dropout=dropout)
        )

    def forward(self, x: torch.Tensor, edge_index: torch.Tensor) -> torch.Tensor:
        """
        Computes the spatial embeddings for all nodes.
        x: [num_nodes, in_channels]
        edge_index: [2, num_edges]
        """
        for i in range(self.num_layers - 1):
            x = F.dropout(x, p=self.dropout, training=self.training)
            x = self.convs[i](x, edge_index)
            x = F.elu(x)
            
        # Final layer
        x = F.dropout(x, p=self.dropout, training=self.training)
        embeddings = self.convs[-1](x, edge_index)
        
        return embeddings
''')

# 2. Models: Classifier
with open("app/ml/models/classifier.py", "w") as f:
    f.write('''"""
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
''')

# 3. Training: Loss
with open("app/ml/training/loss.py", "w") as f:
    f.write('''"""
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
''')

# 4. Evaluation: Metrics
with open("app/ml/evaluation/metrics.py", "w") as f:
    f.write('''"""
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
''')

# 5. Training: Trainer
with open("app/ml/training/trainer.py", "w") as f:
    f.write('''"""
app/ml/training/trainer.py
Training Module orchestrating the forward/backward passes and evaluation.
"""
import torch
from torch.optim import Adam
from typing import Dict, Any

class ModelTrainer:
    def __init__(self, model, classification_head, lr=0.001, pos_weight=10.0, device='cpu'):
        self.model = model.to(device)
        self.head = classification_head.to(device)
        self.device = device
        
        self.optimizer = Adam(
            list(self.model.parameters()) + list(self.head.parameters()), 
            lr=lr, 
            weight_decay=1e-4
        )
        from app.ml.training.loss import WeightedBCELoss
        self.criterion = WeightedBCELoss(pos_weight=pos_weight).to(device)
        
    def train_step(self, data) -> float:
        self.model.train()
        self.head.train()
        self.optimizer.zero_grad()
        
        data = data.to(self.device)
        
        # Forward pass (Spatial embeddings)
        embeddings = self.model(data.x, data.edge_index)
        
        # We only calculate loss for labeled nodes (e.g., the token contract node itself)
        # Assuming data.train_mask exists for this baseline
        logits = self.head(embeddings)
        
        loss = self.criterion(logits[data.train_mask], data.y[data.train_mask].unsqueeze(1).float())
        
        loss.backward()
        
        # Gradient Clipping
        torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
        torch.nn.utils.clip_grad_norm_(self.head.parameters(), max_norm=1.0)
        
        self.optimizer.step()
        
        return loss.item()
''')

# 6. Checkpoints
with open("app/ml/training/checkpoints.py", "w") as f:
    f.write('''"""
app/ml/training/checkpoints.py
Model Checkpoint Manager.
"""
import torch
import os

class CheckpointManager:
    @staticmethod
    def save(model, head, optimizer, epoch, val_loss, filepath="checkpoints/best_model.pth"):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        torch.save({
            'epoch': epoch,
            'model_state_dict': model.state_dict(),
            'head_state_dict': head.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'val_loss': val_loss
        }, filepath)
        
    @staticmethod
    def load(model, head, optimizer, filepath="checkpoints/best_model.pth"):
        if os.path.exists(filepath):
            checkpoint = torch.load(filepath)
            model.load_state_dict(checkpoint['model_state_dict'])
            head.load_state_dict(checkpoint['head_state_dict'])
            if optimizer:
                optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
            return checkpoint['epoch'], checkpoint['val_loss']
        return 0, float('inf')
''')

# Inits
for d in directories:
    with open(f"{d}/__init__.py", "w") as f: pass

print("Generated GATv2 Deep Learning Module.")
