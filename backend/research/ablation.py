import json
import os
import sys
import uuid
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline import run_pipeline
from session.memory import clear_session, get_prev_risk
import pipeline

# Mock LLM generation for speed
pipeline.generate_response = lambda text: "Mocked LLM response"

DATA_FILE = os.path.join(os.path.dirname(__file__), "test_dataset.json")

def get_metrics(y_true, y_scores, threshold=0.65):
    y_pred = [1 if s >= threshold else 0 for s in y_scores]
    try: auc = roc_auc_score(y_true, y_scores)
    except: auc = np.nan
    rec = recall_score(y_true, y_pred, zero_division=0)
    prec = precision_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    
    positives = sum(y_true)
    negatives = len(y_true) - positives
    fpr = sum((p == 1 and t == 0) for p, t in zip(y_pred, y_true)) / negatives if negatives > 0 else 0.0
    
    return auc, rec, prec, fpr, f1

def custom_fusion(deberta_score, feats, deberta_weight, behav_weight, drop_feat=None, use_gating_rule=False):
    f = dict(feats)
    if drop_feat: f[drop_feat] = 0.0
    
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

def run_ablation():
    with open(DATA_FILE, "r") as f: dataset = json.load(f)
    
    X_raw = []
    y_true = []
    categories = []
    
    print(f"Phase 1: Extracting features across {len(dataset)} examples...")
    for idx, ex in enumerate(dataset):
        label = 1 if ex["label"] == "INJECTION" else 0
        cat = ex["category"]
        
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
        categories.append(cat)
        print(f"Processed {idx+1}/{len(dataset)}...", end="\r")
        
    print("\n\nPhase 2: Running Analysis...")
    
    feat_names = ["deberta_score", "role_shift_counter", "conversation_trajectory", 
                  "attack_pattern_similarity", "probing_similarity", "repetition_similarity", 
                  "flag_rate", "escalation_rate", "prev_risk"]
    
    X_mat = np.array([[x[f] for f in feat_names] for x in X_raw])
    y_arr = np.array(y_true)
    
    # Train Logistic Regression
    lr = LogisticRegression(class_weight='balanced', max_iter=500)
    lr.fit(X_mat, y_arr)
    lr_probs = lr.predict_proba(X_mat)[:, 1]
    
    # --- Behavioral-Only Threshold Analysis ---
    print("\n--- Behavioral-Only Threshold Analysis ---")
    behav_scores = [custom_fusion(0.0, x, 0.0, 1.0) for x in X_raw]
    for t in [0.65, 0.35, 0.20, 0.10, 0.05]:
        auc, rec, prec, fpr, f1 = get_metrics(y_true, behav_scores, threshold=t)
        print(f"Threshold {t:.2f} -> Precision: {prec:.4f} | Recall: {rec:.4f} | F1: {f1:.4f} | FPR: {fpr:.4f}")

    # --- Logistic Regression Coefficients ---
    print("\n--- Logistic Regression Learned Coefficients ---")
    print(f"{'Feature'.ljust(30)} | {'Learned Weight'.rjust(15)}")
    print("-" * 50)
    for name, coef in zip(feat_names, lr.coef_[0]):
        print(f"{name.ljust(30)} | {coef:15.4f}")
    print(f"{'Intercept'.ljust(30)} | {lr.intercept_[0]:15.4f}")
    
    results = {}
    def evaluate_setup(name, scores):
        auc, rec, prec, fpr, f1 = get_metrics(y_true, scores)
        # Escalation stress test isolate
        esc_idx = [i for i, c in enumerate(categories) if c == "multi_turn_escalation"]
        esc_y = [y_true[i] for i in esc_idx]
        esc_scores = [scores[i] for i in esc_idx]
        _, esc_rec, _, _, _ = get_metrics(esc_y, esc_scores)
        results[name] = {"AUC": auc, "F1": f1, "Precision": prec, "Recall": rec, "FPR": fpr, "Escalation_Recall": esc_rec}

    # Configurations
    scores = [custom_fusion(x["deberta_score"], x, 0.55, 0.45) for x in X_raw]
    evaluate_setup("Sentinel (Hand-Tuned Baseline 55/45)", scores)
    
    scores = [custom_fusion(x["deberta_score"], x, 0.25, 0.75) for x in X_raw]
    evaluate_setup("Sentinel (Retuned 25/75)", scores)
    
    scores = [custom_fusion(x["deberta_score"], x, 0.55, 0.45, use_gating_rule=True) for x in X_raw]
    evaluate_setup("Sentinel (Baseline + Nonlinear Gate)", scores)
    
    evaluate_setup("Sentinel (Logistic Regression)", lr_probs)
    
    scores = [x["deberta_score"] for x in X_raw]
    evaluate_setup("DeBERTa Only", scores)
    
    evaluate_setup("Behavioral Features Only", behav_scores)
        
    print("\n\n### Ablation Study Results\n")
    print("| Configuration | Overall AUC | Overall F1 | Overall Precision | Overall Recall | Overall FPR | Escalation Stress Test (Recall) |")
    print("|---|---|---|---|---|---|---|")
    for name, r in results.items():
        auc = f"{r['AUC']:.4f}" if not np.isnan(r['AUC']) else "N/A"
        f1 = f"{r['F1']:.4f}"
        prec = f"{r['Precision']:.4f}"
        rec = f"{r['Recall']:.4f}"
        fpr = f"{r['FPR']:.4f}"
        esc = f"{r['Escalation_Recall']:.4f}"
        print(f"| {name} | {auc} | {f1} | {prec} | {rec} | {fpr} | **{esc}** |")

    with open("ablation_results.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    run_ablation()
