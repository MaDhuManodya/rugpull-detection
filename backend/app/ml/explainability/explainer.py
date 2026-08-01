"""
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
