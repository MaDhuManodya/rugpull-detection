import os

os.makedirs("app/ml/models", exist_ok=True)
os.makedirs("app/ml/explainability", exist_ok=True)

# 1. Pipeline Model
with open("app/ml/models/pipeline.py", "w") as f:
    f.write('''"""
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
''')

# 2. Explainability
with open("app/ml/explainability/explainer.py", "w") as f:
    f.write('''"""
app/ml/explainability/explainer.py
Dual Explainability Layer combining SHAP and GNNExplainer.
"""
import torch
try:
    from torch_geometric.explain import Explainer, GNNExplainer
    import shap
except ImportError:
    pass

class DualExplainer:
    def __init__(self, model: torch.nn.Module, device: str = 'cpu'):
        self.model = model.to(device)
        self.device = device
        
        # Initialize GNNExplainer for structural explanation
        try:
            self.gnn_explainer = Explainer(
                model=self.model,
                algorithm=GNNExplainer(epochs=200),
                explanation_type='model',
                node_mask_type='object',
                edge_mask_type='object',
                model_config=dict(
                    mode='binary_classification',
                    task_level='node',
                    return_type='probs',
                )
            )
        except NameError:
            self.gnn_explainer = None

    def explain_structure(self, x, edge_index, target_node: int):
        """
        Identifies the critical subgraph (wallets/transactions) that drove the prediction.
        """
        if not self.gnn_explainer:
            return {"error": "PyG Explainer not available"}
            
        # Generate explanation for the specific target node (usually the token contract)
        explanation = self.gnn_explainer(x, edge_index, index=target_node)
        
        # Extract the most important edges
        edge_mask = explanation.edge_mask
        top_k = torch.topk(edge_mask, min(10, edge_mask.size(0)))
        
        important_edges = []
        for i in range(len(top_k.indices)):
            idx = top_k.indices[i].item()
            score = top_k.values[i].item()
            src = edge_index[0, idx].item()
            dst = edge_index[1, idx].item()
            important_edges.append({"src": src, "dst": dst, "importance": score})
            
        return {"important_edges": important_edges}
        
    def explain_features(self, x_background, x_target):
        """
        Uses SHAP to identify which of the 22 features were most responsible.
        """
        try:
            # SHAP DeepExplainer expects a functional wrapper if the model signature is complex
            # This is a simplified wrapper for feature explanation
            explainer = shap.DeepExplainer(self.model.gatv2, x_background)
            shap_values = explainer.shap_values(x_target)
            return {"shap_values": shap_values}
        except NameError:
            return {"error": "SHAP not available"}
''')

# Inits
with open("app/ml/explainability/__init__.py", "w") as f: pass

print("Generated Pipeline and Explainability Modules.")
