import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, average_precision_score, matthews_corrcoef, confusion_matrix

RESULTS_DIR = "submission_assets/results"
ASSETS_DIR = "submission_assets/chapter5_assets"
FIG_DIR = os.path.join(ASSETS_DIR, "figures")
TBL_DIR = os.path.join(ASSETS_DIR, "tables")

for d in [RESULTS_DIR, FIG_DIR, TBL_DIR]:
    os.makedirs(d, exist_ok=True)

sns.set_theme(style="whitegrid")
plt.rcParams.update({'font.size': 12, 'font.family': 'serif'})

def save_fig(name):
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, f"{name}.png"), dpi=300)
    plt.savefig(os.path.join(FIG_DIR, f"{name}.svg"), format="svg")
    plt.close()

# Load Data
train_df = pd.read_csv("datasets/processed/train.csv")
test_df = pd.read_csv("datasets/processed/test.csv")

# Null Feature Matrix (Because API Data Collection Failed)
X_train = np.ones((len(train_df), 1))
y_train = train_df['rugpull_label'].values
X_test = np.ones((len(test_df), 1))
y_test = test_df['rugpull_label'].values

def calc_specificity(y_true, y_pred):
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0,1]).ravel()
    return tn / (tn + fp) if (tn + fp) > 0 else 0.0

models_to_run = {
    "Random Forest": RandomForestClassifier(n_estimators=10, random_state=42),
    "XGBoost": GradientBoostingClassifier(n_estimators=10, random_state=42)
}

failed_models = ["GAT", "GATv2", "TGN", "Proposed Framework (GATv2 + TGN + Fusion)"]

results = []
roc_curves = {}

# Train ML Models
for name, model in models_to_run.items():
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    preds_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, 'predict_proba') else preds
    
    results.append({
        "Model": name,
        "Accuracy": accuracy_score(y_test, preds),
        "Precision": precision_score(y_test, preds, zero_division=0),
        "Recall": recall_score(y_test, preds, zero_division=0),
        "F1-score": f1_score(y_test, preds, zero_division=0),
        "ROC-AUC": roc_auc_score(y_test, preds_proba) if len(np.unique(preds_proba)) > 1 else 0.5,
        "PR-AUC": average_precision_score(y_test, preds_proba),
        "Specificity": calc_specificity(y_test, preds),
        "Sensitivity": recall_score(y_test, preds, zero_division=0), # Sensitivity is Recall
        "Matthews Correlation Coefficient": matthews_corrcoef(y_test, preds)
    })
    
# Append Failed GNN Models
for name in failed_models:
    results.append({
        "Model": name,
        "Accuracy": "N/A – evaluation could not be completed",
        "Precision": "N/A – evaluation could not be completed",
        "Recall": "N/A – evaluation could not be completed",
        "F1-score": "N/A – evaluation could not be completed",
        "ROC-AUC": "N/A – evaluation could not be completed",
        "PR-AUC": "N/A – evaluation could not be completed",
        "Specificity": "N/A – evaluation could not be completed",
        "Sensitivity": "N/A – evaluation could not be completed",
        "Matthews Correlation Coefficient": "N/A – evaluation could not be completed"
    })

df_results = pd.DataFrame(results)
df_results.to_csv(os.path.join(RESULTS_DIR, "model_comparison.csv"), index=False)
df_results.to_csv(os.path.join(RESULTS_DIR, "baseline_metrics.csv"), index=False)

# Table 5.9
table5_9 = df_results[["Model", "Accuracy", "Precision", "Recall", "F1-score", "ROC-AUC"]]
table5_9.to_csv(os.path.join(TBL_DIR, "table5_9.csv"), index=False)
with open(os.path.join(TBL_DIR, "table5_9.md"), "w") as f:
    f.write(table5_9.to_markdown(index=False))

# Figures
def safe_float(val):
    try: return float(val)
    except: return 0.0

plot_df = df_results.copy()
for col in ["Accuracy", "F1-score", "ROC-AUC"]:
    plot_df[col] = plot_df[col].apply(safe_float)

# Fig 5.14 ROC Comparison
plt.figure(figsize=(8,5))
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Random Guess (AUC=0.5)')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Figure 5.14: ROC Comparison (All Models)')
plt.legend(loc="lower right")
save_fig("Figure_5.14_ROC_Comparison")

# Fig 5.15 Bar Chart F1
plt.figure(figsize=(10,6))
sns.barplot(data=plot_df, x="Model", y="F1-score")
plt.xticks(rotation=45, ha="right")
plt.title("Figure 5.15: F1-score Comparison")
plt.tight_layout()
save_fig("Figure_5.15_F1_Score_Comparison")

# Fig 5.16 Bar Chart Accuracy
plt.figure(figsize=(10,6))
sns.barplot(data=plot_df, x="Model", y="Accuracy")
plt.xticks(rotation=45, ha="right")
plt.title("Figure 5.16: Accuracy Comparison")
plt.tight_layout()
save_fig("Figure_5.16_Accuracy_Comparison")

# Interpretation MD
interp_md = """# Table 5.9 Interpretation

## Model Performance Analysis
The evaluation of the baseline models reveals a critical constraint in the experimental environment: due to the absence of valid API data collection, all traditional machine learning baselines (Random Forest and XGBoost) were forced to train on a null feature space. Consequently, both Random Forest and XGBoost achieved identical performance, mathematically defaulting to the majority class prediction. 

Neither model performed "best" in a discriminative sense, as both achieved a ROC-AUC of exactly 0.50, representing random guessing.

## Graph and Temporal Model Evaluation
As explicitly documented in Table 5.9, the evaluation for **GAT**, **GATv2**, **TGN**, and the **Proposed Framework (GATv2 + TGN + Fusion)** could not be completed. 
Because graph neural networks fundamentally require structural data (nodes, edge connectivity matrices, and temporal transaction links), the total failure of the API collection pipeline meant that no graph could be constructed. Therefore, it is impossible to claim that GATv2 outperformed GAT, or that temporal modelling improved performance, as the models could not be compiled or executed. The Proposed Framework did not achieve the best overall performance because its execution was entirely blocked by the absence of data.
"""
with open(os.path.join(ASSETS_DIR, "tables", "table5_9_interpretation.md"), "w") as f:
    f.write(interp_md)

# Report MD
report_md = """# Model Comparison Report: Graph Framework Evaluation Failure

## Incident Summary
During the final experimental evaluation phase, the traditional tabular machine learning baselines (Random Forest and XGBoost) were executed successfully, albeit on a zero-feature dataset resulting in 0.50 ROC-AUC baseline performance.

However, the core topological models of this thesis—**Graph Attention Network (GAT)**, **Graph Attention Network v2 (GATv2)**, **Temporal Graph Network (TGN)**, and the **Proposed Framework**—could not be evaluated.

## Technical Reason for "N/A" Result
Graph Neural Networks operate by passing messages across defined edges between nodes (e.g., wallet addresses and smart contracts). 
Because the Etherscan and BscScan API keys were not provided to the execution environment, the data collection script (`phase2_collect.py`) failed to extract any blockchain transactions, token transfers, or contract interactions. 

Without this data, it is mathematically impossible to construct an `edge_index` tensor or a temporal event stream. A Graph Neural Network cannot be trained on a graph containing zero edges and zero node features. 

Therefore, in strict adherence to the non-fabrication protocols of this thesis, no placeholder data was synthesized to force the models to compile. The evaluation for these models was formally aborted, and their results have been accurately recorded as **"N/A – evaluation could not be completed"** in all subsequent tables and metrics.
"""
with open(os.path.join(RESULTS_DIR, "model_comparison_report.md"), "w") as f:
    f.write(report_md)

print("Final Baselines and Reports Generated Successfully.")
