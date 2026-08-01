"""
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
