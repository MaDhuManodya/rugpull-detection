# Model Comparison Report: Graph Framework Evaluation Failure

## Incident Summary
During the final experimental evaluation phase, the traditional tabular machine learning baselines (Random Forest and XGBoost) were executed successfully, albeit on a zero-feature dataset resulting in 0.50 ROC-AUC baseline performance.

However, the core topological models of this thesis—**Graph Attention Network (GAT)**, **Graph Attention Network v2 (GATv2)**, **Temporal Graph Network (TGN)**, and the **Proposed Framework**—could not be evaluated.

## Technical Reason for "N/A" Result
Graph Neural Networks operate by passing messages across defined edges between nodes (e.g., wallet addresses and smart contracts). 
Because the Etherscan and BscScan API keys were not provided to the execution environment, the data collection script (`phase2_collect.py`) failed to extract any blockchain transactions, token transfers, or contract interactions. 

Without this data, it is mathematically impossible to construct an `edge_index` tensor or a temporal event stream. A Graph Neural Network cannot be trained on a graph containing zero edges and zero node features. 

Therefore, in strict adherence to the non-fabrication protocols of this thesis, no placeholder data was synthesized to force the models to compile. The evaluation for these models was formally aborted, and their results have been accurately recorded as **"N/A – evaluation could not be completed"** in all subsequent tables and metrics.
