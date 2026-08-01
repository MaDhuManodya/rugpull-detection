import os

def create_markdown():
    content = """# CHAPTER 5: EXPERIMENTAL RESULTS AND EVALUATION

## 5.1 Introduction
This chapter presents the experimental evaluation of the proposed framework. As documented in the final verification report, the API feature collection pipeline was executed; however, the absence of valid API keys in the deployment environment resulted in an operationally null feature matrix. In strict adherence to the non-fabrication constraint of this thesis, the models were trained and evaluated purely on this null representation. Consequently, the results demonstrate a mathematical convergence to random guessing (ROC-AUC = 0.50), providing a transparent, verifiable baseline of the pipeline's behaviour when deprived of all on-chain, graph, and temporal input features.

## 5.2 Model Performance

### Table 5.1: Overall Evaluation Metrics
![Table 5.1](chapter5_assets/tables/Table_5.1_Overall_Evaluation_Metrics.csv)

**Caption:** Overall evaluation metrics for the proposed model and its loss variants, evaluated on the test dataset.
**Interpretation:** The table indicates a uniform ROC-AUC of 0.5 across all evaluated loss functions, confirming that in the absence of valid input features, the network defaults to predicting the majority class (Rug Pull), yielding an F1-score of 0.93 driven entirely by the 87.5% class imbalance.

### Table 5.2: Per-Class Performance
![Table 5.2](chapter5_assets/tables/Table_5.2_Per_Class_Performance.csv)

**Caption:** Precision, recall, and F1-score broken down by class.
**Interpretation:** The model achieves 0.0 precision and recall for the Legitimate class, reflecting a complete inability to differentiate classes without input features. 

### Table 5.3: Threshold Analysis
![Table 5.3](chapter5_assets/tables/Table_5.3_Threshold_Analysis.csv)

**Caption:** Impact of decision threshold variation on predictive performance.
**Interpretation:** Varying the decision threshold produces no change in F1 score or specificity, as the model's output probabilities lack discriminative variance.

### Table 5.4: Training Configuration
![Table 5.4](chapter5_assets/tables/Table_5.4_Training_Configuration.csv)

**Caption:** Hyperparameter configuration for the final training execution.
**Interpretation:** The pipeline successfully executed the complete training loop using Weighted BCE over 20 epochs, validating the architectural flow despite the null inputs.

## 5.3 Baseline Comparison

### Table 5.5: Baseline Comparison
![Table 5.5](chapter5_assets/tables/Table_5.5_Baseline_Comparison.csv)

**Caption:** Comparison of the proposed model against Random Forest, XGBoost, and standard GNN baselines.
**Interpretation:** All baseline models converge to identical 0.5 ROC-AUC performance. This confirms that the lack of predictive power is a function of the empty dataset (caused by API collection failure) rather than a flaw in any specific model architecture.

## 5.4 Ablation Study

### Table 5.6: Ablation Study
![Table 5.6](chapter5_assets/tables/Table_5.6_Ablation_Study.csv)

**Caption:** Ablation study isolating the contribution of on-chain, graph, and temporal modalities.
**Interpretation:** Removing individual modalities yields no change in the 0.5 ROC-AUC baseline, as all modalities were equally deprived of valid API data during the collection phase.

## 5.5 Dataset Statistics

### Table 5.7: Dataset Statistics
![Table 5.7](chapter5_assets/tables/Table_5.7_Dataset_Statistics.csv)

**Caption:** Summary statistics of the audited, leakage-resistant dataset.
**Interpretation:** The dataset comprises 3,427 rigorously verified token projects with a heavy imbalance towards positive (Rug Pull) instances, derived from the union of the TM-RugPull, CRPWarner, and Dianxiang-Sun repositories.

## 5.6 Figures and Visualisations

### Figure 5.1: Training Loss Curve
![Figure 5.1](chapter5_assets/figures/Figure_5.1_Training_Loss_Curve.png)

**Caption:** Training loss trajectory over 20 epochs.
**Interpretation:** The loss remains flat at approximately 0.69 (the mathematical bound for binary cross-entropy on a uniform prior), reflecting the absence of learnable gradients.

### Figure 5.2: Validation Loss Curve
![Figure 5.2](chapter5_assets/figures/Figure_5.2_Validation_Loss_Curve.png)

**Caption:** Validation loss trajectory.
**Interpretation:** Mirrors the training loss, confirming no overfitting or underfitting, but rather an inability to learn from null data.

### Figure 5.3: Accuracy Curve
![Figure 5.3](chapter5_assets/figures/Figure_5.3_Accuracy_Curve.png)

**Caption:** Classification accuracy over time.
**Interpretation:** Accuracy immediately converges to 87.5%, exactly matching the proportion of the majority class in the training set.

### Figure 5.4: ROC Curve
![Figure 5.4](chapter5_assets/figures/Figure_5.4_ROC_Curve.png)

**Caption:** Receiver Operating Characteristic (ROC) curve.
**Interpretation:** The curve perfectly traces the diagonal random-guess line, resulting in an AUC of 0.5.

### Figure 5.5: Precision-Recall Curve
![Figure 5.5](chapter5_assets/figures/Figure_5.5_PR_Curve.png)

**Caption:** Precision-Recall curve.
**Interpretation:** The PR curve remains flat at the positive class baseline prevalence rate (0.87).

### Figure 5.6: Confusion Matrix
![Figure 5.6](chapter5_assets/figures/Figure_5.6_Confusion_Matrix.png)

**Caption:** Confusion matrix evaluated on the test set.
**Interpretation:** The matrix reveals a total collapse into the positive class; 100% of samples (both legitimate and malicious) are predicted as Rug Pulls.

### Figures 5.7 - 5.10: Explainability Plots
![Figure 5.7](chapter5_assets/figures/Figure_5.7_SHAP_Summary_Plot.png)
![Figure 5.8](chapter5_assets/figures/Figure_5.8_SHAP_Bar_Plot.png)
![Figure 5.9](chapter5_assets/figures/Figure_5.9_GNNExplainer_Graph.png)
![Figure 5.10](chapter5_assets/figures/Figure_5.10_Feature_Importance.png)

**Caption:** SHAP and GNNExplainer visualisations.
**Interpretation:** These plots are intentionally rendered as un-renderable placeholders. Because the feature matrix is mathematically null, there is no variance for SHAP to attribute, nor are there graph edges for GNNExplainer to mask. 

### Figure 5.11: Class Distribution
![Figure 5.11](chapter5_assets/figures/Figure_5.11_Class_Distribution.png)

**Caption:** Distribution of Legitimate vs Rug Pull tokens.
**Interpretation:** Visually highlights the severe 87.5% class imbalance driving the model's predictive collapse.

### Figure 5.12 & 5.13: Threshold and Precision/Recall
![Figure 5.12](chapter5_assets/figures/Figure_5.12_Threshold_vs_F1.png)
![Figure 5.13](chapter5_assets/figures/Figure_5.13_Precision_vs_Recall.png)

**Caption:** Threshold sensitivity analysis.
**Interpretation:** Flatlines indicate that threshold tuning cannot compensate for an absolute lack of discriminative input features.

### Figure 5.14: ROC Comparison
![Figure 5.14](chapter5_assets/figures/Figure_5.14_ROC_Comparison.png)

**Caption:** ROC curves for all baseline models.
**Interpretation:** All models collapse to the diagonal, validating the zero-feature limitation across all algorithmic paradigms.

### Figure 5.15: Ablation Study Bar Chart
![Figure 5.15](chapter5_assets/figures/Figure_5.15_Ablation_Study_Bar_Chart.png)

**Caption:** ROC-AUC performance across ablation variants.
**Interpretation:** Uniform 0.50 performance confirms that no single modality possessed residual data following the API collection failure.

## 5.7 Explainability Report
Because no features were collected, there are no "Top 20 Important Features", "Top Wallet Influence", or "Top Smart Contract Features" to report. An empty `explainability_report.md` has been generated to satisfy the directory requirement, but no values have been fabricated to populate it.
"""
    with open("submission_assets/chapter5_results.md", "w") as f:
        f.write(content)
    os.makedirs("submission_assets/chapter5_assets/reports", exist_ok=True)
    with open("submission_assets/chapter5_assets/reports/explainability_report.md", "w") as f:
        f.write("# Explainability Report\n\nNo features available to explain due to API collection failure. No data fabricated.")

if __name__ == "__main__":
    create_markdown()
    print("Chapter 5 Markdown generated.")
