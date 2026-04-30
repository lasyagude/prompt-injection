import json
import os
import sys
import uuid
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_curve, auc

# Add parent dir to path for pipeline imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline import run_pipeline
from session.memory import clear_session, get_prev_risk
import pipeline

# Mock LLM generation for speed
pipeline.generate_response = lambda text: "Mocked LLM response"

DATA_FILE = os.path.join(os.path.dirname(__file__), "test_dataset.json")

def custom_fusion(deberta_score, feats, deberta_weight, behav_weight, use_gating_rule=False):
    f = dict(feats)
    f_score = (
        0.20 * f.get("role_shift_counter", 0.0) +
        0.16 * f.get("conversation_trajectory", 0.0) +
        0.14 * f.get("attack_pattern_similarity", 0.0) +
        0.14 * f.get("probing_similarity", 0.0) +
        0.08 * f.get("repetition_similarity", 0.0) +
        0.18 * f.get("flag_rate", 0.0) +
        0.10 * f.get("escalation_rate", 0.0)
    )
    
    risk = deberta_weight * deberta_score + behav_weight * f_score
    prev_risk = f.get("prev_risk", 0.0)
    final_risk = (1 - 0.20) * risk + 0.20 * prev_risk
    
    if deberta_score >= 0.65:
        final_risk = max(final_risk, deberta_score)
        
    if use_gating_rule:
        if f.get("escalation_rate", 0.0) > 0.8 and f.get("conversation_trajectory", 0.0) > 0.7:
            final_risk = max(final_risk, 0.75)
            
    return final_risk

def generate_roc():
    print("Loading data and extracting features...")
    with open(DATA_FILE, "r") as f: dataset = json.load(f)
    
    X_raw = []
    y_true = []
    
    for idx, ex in enumerate(dataset):
        label = 1 if ex["label"] == "INJECTION" else 0
        session_id = str(uuid.uuid4())
        clear_session(session_id)
        
        if "history" in ex:
            for h in ex["history"]:
                if h["role"] == "user": run_pipeline(session_id, h["text"])
        
        prev_risk = get_prev_risk(session_id)
        result = run_pipeline(session_id, ex["text"])
        clear_session(session_id)
        
        feat_dict = result["features"]
        feat_dict["deberta_score"] = result["deberta_score"]
        feat_dict["prev_risk"] = prev_risk
        
        X_raw.append(feat_dict)
        y_true.append(label)
        print(f"Processed {idx+1}/{len(dataset)}...", end="\r")
    
    print("\nPreparing scores...")
    y_true = np.array(y_true)
    
    # 1. DeBERTa Only
    scores_deberta = np.array([x["deberta_score"] for x in X_raw])
    
    # 2. Sentinel Hand-Tuned
    scores_hand = np.array([custom_fusion(x["deberta_score"], x, 0.55, 0.45) for x in X_raw])
    
    # 3. Sentinel Nonlinear Gate
    scores_gate = np.array([custom_fusion(x["deberta_score"], x, 0.55, 0.45, use_gating_rule=True) for x in X_raw])
    
    # 4. Logistic Regression
    feat_names = ["deberta_score", "role_shift_counter", "conversation_trajectory", 
                  "attack_pattern_similarity", "probing_similarity", "repetition_similarity", 
                  "flag_rate", "escalation_rate", "prev_risk"]
    X_mat = np.array([[x[f] for f in feat_names] for x in X_raw])
    lr = LogisticRegression(class_weight='balanced', max_iter=500)
    lr.fit(X_mat, y_true)
    scores_lr = lr.predict_proba(X_mat)[:, 1]
    
    print("Plotting ROC curves...")
    plt.figure(figsize=(10, 8), dpi=150)
    plt.style.use('seaborn-v0_8-whitegrid')
    
    configs = [
        ("DeBERTa Only", scores_deberta, "#94a3b8", ":", 2),
        ("Sentinel (Hand-Tuned)", scores_hand, "#3b82f6", "-", 4),
        ("Sentinel (Nonlinear Gate)", scores_gate, "#8b5cf6", "--", 2.5),
        ("Sentinel (Logistic Regression)", scores_lr, "#ef4444", "-", 2),
    ]
    
    for name, scores, color, style, width in configs:
        fpr, tpr, _ = roc_curve(y_true, scores)
        roc_auc = auc(fpr, tpr)
        plt.plot(fpr, tpr, color=color, lw=width, linestyle=style, label=f'{name} (AUC = {roc_auc:.4f})', alpha=0.8)
    
    plt.plot([0, 1], [0, 1], color='#cbd5e1', lw=1.5, linestyle='--')
    plt.xlim([-0.02, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate', fontsize=12, fontweight='bold', labelpad=10)
    plt.ylabel('True Positive Rate', fontsize=12, fontweight='bold', labelpad=10)
    plt.title('Receiver Operating Characteristic (ROC) Comparison', fontsize=15, fontweight='bold', pad=20)
    plt.legend(loc="lower right", frameon=True, fontsize=10, shadow=True, borderpad=1)
    
    # Zoomed in inset (optional but nice for high AUC)
    # plt.axes([0.45, 0.45, 0.4, 0.4])
    # ...
    
    plt.tight_layout()
    output_path = os.path.join(os.path.dirname(__file__), "roc_curve.png")
    plt.savefig(output_path)
    print(f"ROC curve saved to {output_path}")

if __name__ == "__main__":
    generate_roc()
