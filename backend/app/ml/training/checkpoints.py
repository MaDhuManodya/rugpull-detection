"""
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
