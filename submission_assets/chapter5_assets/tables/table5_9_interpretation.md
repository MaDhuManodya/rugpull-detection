# Table 5.9 Interpretation

## Model Performance Analysis
The evaluation of the baseline models reveals a critical constraint in the experimental environment: due to the absence of valid API data collection, all traditional machine learning baselines (Random Forest and XGBoost) were forced to train on a null feature space. Consequently, both Random Forest and XGBoost achieved identical performance, mathematically defaulting to the majority class prediction. 

Neither model performed "best" in a discriminative sense, as both achieved a ROC-AUC of exactly 0.50, representing random guessing.

## Graph and Temporal Model Evaluation
As explicitly documented in Table 5.9, the evaluation for **GAT**, **GATv2**, **TGN**, and the **Proposed Framework (GATv2 + TGN + Fusion)** could not be completed. 
Because graph neural networks fundamentally require structural data (nodes, edge connectivity matrices, and temporal transaction links), the total failure of the API collection pipeline meant that no graph could be constructed. Therefore, it is impossible to claim that GATv2 outperformed GAT, or that temporal modelling improved performance, as the models could not be compiled or executed. The Proposed Framework did not achieve the best overall performance because its execution was entirely blocked by the absence of data.
