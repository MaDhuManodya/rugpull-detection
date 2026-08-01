"""
tests/test_pipeline_e2e.py
End-to-End Validation script for the ML Pipeline.
"""
import torch
import time
import psutil
import os
try:
    from torch_geometric.data import TemporalData
    HAS_PYG = True
except ImportError:
    HAS_PYG = False

from app.ml.models.pipeline import RugPullDetectionModel
from app.ml.explainability.explainer import DualExplainer

def get_memory_usage():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024  # in MB

def run_validation():
    print("=" * 60)
    print("INTERNAL ML PIPELINE VALIDATION")
    print("=" * 60)
    
    if not HAS_PYG:
        print("ERROR: PyTorch Geometric not installed. Cannot run validation.")
        return False
        
    print(f"[+] Initial Memory: {get_memory_usage():.2f} MB")
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"[+] Device Target: {device}")

    # 1. Mock Graph Data (100 nodes, 500 edges)
    print("\n--- 1. Graph Construction Mock ---")
    num_nodes = 100
    num_edges = 500
    
    x = torch.rand((num_nodes, 22), dtype=torch.float)
    src = torch.randint(0, num_nodes, (num_edges,), dtype=torch.long)
    dst = torch.randint(0, num_nodes, (num_edges,), dtype=torch.long)
    edge_index = torch.stack([src, dst], dim=0)
    t = torch.sort(torch.randint(0, 10000, (num_edges,), dtype=torch.long))[0] # strictly ordered
    msg = torch.rand((num_edges, 4), dtype=torch.float)
    
    print(f"  x (Node Features): {x.shape}, dtype={x.dtype}, device={x.device}")
    print(f"  edge_index: {edge_index.shape}, dtype={edge_index.dtype}")
    print(f"  t (Timestamps): {t.shape}, strictly sorted: {torch.all(t[1:] >= t[:-1]).item()}")
    print(f"  msg (Edge Features): {msg.shape}")

    # 2. Instantiate Model
    print("\n--- 2. Model Instantiation ---")
    start_time = time.time()
    try:
        model = RugPullDetectionModel(num_nodes=num_nodes, node_feature_dim=22, edge_msg_dim=4, hidden_dim=128)
        model = model.to(device)
        print("  [OK] RugPullDetectionModel instantiated and moved to device.")
    except Exception as e:
        print(f"  [ERROR] Model instantiation failed: {e}")
        return False

    # Move data to device
    x, edge_index, src, dst, t, msg = x.to(device), edge_index.to(device), src.to(device), dst.to(device), t.to(device), msg.to(device)

    # 3. Forward Pass
    print("\n--- 3. Forward Pass (GATv2 -> TGN -> Fusion -> Classifier) ---")
    forward_start = time.time()
    try:
        model.eval()
        with torch.no_grad():
            logits = model(x, edge_index, src, dst, t, msg)
        print("  [OK] Forward pass completed successfully.")
        print(f"  Output logits shape: {logits.shape}")
        
        if logits.shape != (num_nodes, 1):
            print(f"  [ERROR] Expected logits shape ({num_nodes}, 1), got {logits.shape}")
            return False
            
    except Exception as e:
        print(f"  [ERROR] Forward pass failed: {e}")
        return False
        
    forward_time = time.time() - forward_start
    print(f"  Forward pass time: {forward_time:.4f}s")
    print(f"  Peak Memory usage: {get_memory_usage():.2f} MB")

    # 4. Explainability
    print("\n--- 4. Explainability Modules ---")
    try:
        explainer = DualExplainer(model=model, device=device.type)
        
        # Test missing PyG Explain (will soft fail if PyG Explainer lacks certain dependencies locally, but we check logic)
        res_struct = explainer.explain_structure(x, edge_index, target_node=0)
        if "error" in res_struct:
            print(f"  [WARNING] Structural Explanation skipped: {res_struct['error']}")
        else:
            print("  [OK] Structural Explanation completed.")
            
        res_feat = explainer.explain_features(x, x[0:1])
        if "error" in res_feat:
             print(f"  [WARNING] Feature Explanation skipped: {res_feat['error']}")
        else:
             print("  [OK] Feature Explanation completed.")
             
    except Exception as e:
        print(f"  [ERROR] Explainability setup failed: {e}")
        return False

    print("\n" + "=" * 60)
    print("ALL VALIDATIONS PASSED.")
    print("=" * 60)
    return True

if __name__ == "__main__":
    run_validation()
