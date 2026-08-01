"""
app/ml/models/pipeline.py
End-to-End Unified Model Architecture.
Chains GATv2 -> TGN -> Fusion -> Classifier.
"""
import torch
import torch.nn as nn
try:
    from torch_geometric.nn.models import TGNMemory
    from torch_geometric.nn.models.tgn import IdentityMessage, LastAggregator
except ImportError:
    pass

from app.ml.models.gatv2 import GATv2SpatialEncoder
from app.ml.models.classifier import BinaryClassificationHead

class AdaptiveFusionLayer(nn.Module):
    def __init__(self, dim: int = 128):
        super().__init__()
        self.gating = nn.Sequential(
            nn.Linear(dim * 2, dim),
            nn.Sigmoid()
        )
        self.proj = nn.Linear(dim * 2, dim)

    def forward(self, spatial_emb: torch.Tensor, temporal_emb: torch.Tensor) -> torch.Tensor:
        combined = torch.cat([spatial_emb, temporal_emb], dim=-1)
        gate = self.gating(combined)
        fused = self.proj(combined)
        return gate * fused

class RugPullDetectionModel(nn.Module):
    def __init__(self, num_nodes: int, node_feature_dim: int = 22, edge_msg_dim: int = 4, hidden_dim: int = 128):
        super().__init__()
        
        # 1. GATv2 Spatial Encoder
        self.gatv2 = GATv2SpatialEncoder(
            in_channels=node_feature_dim, 
            hidden_channels=hidden_dim, 
            out_channels=hidden_dim
        )
        
        # 2. Temporal Memory (TGN)
        try:
            self.memory = TGNMemory(
                num_nodes=num_nodes,
                raw_msg_dim=edge_msg_dim,
                memory_dim=hidden_dim,
                time_dim=32,
                message_module=IdentityMessage(raw_msg_dim=edge_msg_dim, memory_dim=hidden_dim, time_dim=32),
                aggregator_module=LastAggregator()
            )
        except NameError:
            self.memory = None # PyG not installed locally
            
        # 3. Fusion Layer
        self.fusion = AdaptiveFusionLayer(dim=hidden_dim)
        
        # 4. Classifier
        self.classifier = BinaryClassificationHead(in_channels=hidden_dim)

    def forward(self, x, edge_index, src, dst, t, msg):
        """
        End-to-end forward pass matching the thesis architecture.
        """
        # Step 1: Spatial Embeddings (Graph Structure)
        spatial_emb = self.gatv2(x, edge_index)
        
        # Step 2: Temporal Memory Update (Event Sequence)
        if self.memory:
            self.memory.update_state(src, dst, t, msg)
            
            # The TGN memory state represents the temporal embedding
            temporal_emb = self.memory(torch.arange(x.size(0), device=x.device))
        else:
            temporal_emb = spatial_emb # Fallback if PyG missing
            
        # Step 3: Multimodal Fusion
        fused_emb = self.fusion(spatial_emb, temporal_emb)
        
        # Step 4: Binary Classification
        logits = self.classifier(fused_emb)
        
        return logits
