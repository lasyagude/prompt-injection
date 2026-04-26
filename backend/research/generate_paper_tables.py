import json
import os
import sys
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score
import warnings

warnings.filterwarnings('ignore')
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pipeline import run_pipeline
from session.memory import clear_session
import pipeline
pipeline.generate_response = lambda text: "Mock"

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

def custom_fusion(deberta_score, feats, deberta_weight, behav_weight, esc_th=None, top_th=None):
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
        
    if esc_th and top_th:
        if f.get("escalation_rate", 0.0) > esc_th and f.get("conversation_trajectory", 0.0) > top_th:
            final_risk = max(final_risk, 0.75)
            
    return final_risk

def run():
    with open(DATA_FILE, "r") as f: dataset = json.load(f)
    X_raw, y_true, categories = [], [], []
    for ex in dataset:
        label = 1 if ex["label"] == "INJECTION" else 0
        session_id = str(np.random.randint(100000))
        clear_session(session_id)
        if "history" in ex:
            for h in ex["history"]:
                if h["role"] == "user": run_pipeline(session_id, h["text"])
        prev_risk = pipeline.get_prev_risk(session_id)
        res = run_pipeline(session_id, ex["text"])
        f = res["features"]
        f["deberta_score"] = res["deberta_score"]
        f["prev_risk"] = prev_risk
        X_raw.append(f)
        y_true.append(label)
        categories.append(ex["category"])

    feat_names = ["deberta_score", "role_shift_counter", "conversation_trajectory", 
                  "attack_pattern_similarity", "probing_similarity", "repetition_similarity", 
                  "flag_rate", "escalation_rate", "prev_risk"]
    
    X_mat = np.array([[x[f] for f in feat_names] for x in X_raw])
    y_arr = np.array(y_true)
    esc_idx = [i for i, c in enumerate(categories) if c == "multi_turn_escalation"]

    # --- Cross Validation Comparison ---
    kf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    cv_data = {
        "Gate": {"f1": [], "prec": [], "rec": [], "esc": []},
        "Logistic Regression": {"f1": [], "prec": [], "rec": [], "esc": []}
    }
    
    for train_idx, test_idx in kf.split(X_raw, y_arr):
        y_test = y_arr[test_idx]
        X_train_fold = X_mat[train_idx]
        y_train_fold = y_arr[train_idx]
        X_test_fold = X_mat[test_idx]
        
        # 1. Gate Fold
        scores_gate = [custom_fusion(X_raw[i]["deberta_score"], X_raw[i], 0.55, 0.45, 0.8, 0.7) for i in test_idx]
        preds_gate = [1 if s >= 0.65 else 0 for s in scores_gate]
        cv_data["Gate"]["f1"].append(f1_score(y_test, preds_gate, zero_division=0))
        cv_data["Gate"]["prec"].append(precision_score(y_test, preds_gate, zero_division=0))
        cv_data["Gate"]["rec"].append(recall_score(y_test, preds_gate, zero_division=0))
        
        # 2. LR Fold
        lr_fold = LogisticRegression(class_weight='balanced', max_iter=500)
        lr_fold.fit(X_train_fold, y_train_fold)
        preds_lr = lr_fold.predict(X_test_fold)
        cv_data["Logistic Regression"]["f1"].append(f1_score(y_test, preds_lr, zero_division=0))
        cv_data["Logistic Regression"]["prec"].append(precision_score(y_test, preds_lr, zero_division=0))
        cv_data["Logistic Regression"]["rec"].append(recall_score(y_test, preds_lr, zero_division=0))

        # Escalation Recall
        fold_esc_idx = [i for i in test_idx if i in esc_idx]
        if fold_esc_idx:
            e_y = [y_arr[i] for i in range(len(y_arr)) if i in fold_esc_idx]
            
            # Gate esc
            e_p_gate = [preds_gate[list(test_idx).index(i)] for i in fold_esc_idx]
            cv_data["Gate"]["esc"].append(recall_score(e_y, e_p_gate, zero_division=0))
            
            # LR esc
            e_p_lr = [preds_lr[list(test_idx).index(i)] for i in fold_esc_idx]
            cv_data["Logistic Regression"]["esc"].append(recall_score(e_y, e_p_lr, zero_division=0))
            
    cv_summary = {}
    for model in cv_data:
        cv_summary[model] = {
            "F1": f"{np.mean(cv_data[model]['f1']):.4f} ± {np.std(cv_data[model]['f1']):.4f}",
            "Precision": f"{np.mean(cv_data[model]['prec']):.4f} ± {np.std(cv_data[model]['prec']):.4f}",
            "Recall": f"{np.mean(cv_data[model]['rec']):.4f} ± {np.std(cv_data[model]['rec']):.4f}",
            "Escalation Recall": f"{np.mean(cv_data[model]['esc']):.4f} ± {np.std(cv_data[model]['esc']):.4f}"
        }

    # --- Logistic Regression Full Coefficients ---
    lr_full = LogisticRegression(class_weight='balanced', max_iter=500)
    lr_full.fit(X_mat, y_arr)
    coef_res = {name: float(coef) for name, coef in zip(feat_names, lr_full.coef_[0])}
    coef_res["Intercept"] = float(lr_full.intercept_[0])

    # --- Write final_model_config.json ---
    config = {
        "thresholds": {"WARN": 0.35, "BLOCK": 0.65},
        "nonlinear_gate": {
            "escalation_threshold": 0.8,
            "topic_shift_threshold": 0.7,
            "override_risk": 0.75
        },
        "logistic_regression": {
            "coefficients": coef_res,
            "feature_order": feat_names
        },
        "fusion_weights": {
            "deberta": 0.55,
            "behavioral": 0.45,
            "history_dampener": 0.20
        }
    }
    with open("final_model_config.json", "w") as f:
        json.dump(config, f, indent=2)

    # --- Primary Model Comparison (Single Run) ---
    lr_probs = lr_full.predict_proba(X_mat)[:, 1]
    models = {
        "Sentinel (Hand-Tuned Baseline)": [custom_fusion(x["deberta_score"], x, 0.55, 0.45) for x in X_raw],
        "Sentinel (Baseline + Nonlinear Gate)": [custom_fusion(x["deberta_score"], x, 0.55, 0.45, 0.8, 0.7) for x in X_raw],
        "Sentinel (Logistic Regression)": lr_probs,
        "DeBERTa Only": [x["deberta_score"] for x in X_raw]
    }
    comp_res = {}
    for name, scores in models.items():
        auc, rec, prec, fpr, f1 = get_metrics(y_true, scores)
        e_y = [y_true[i] for i in esc_idx]
        e_scores = [scores[i] for i in esc_idx]
        _, e_rec, _, _, _ = get_metrics(e_y, e_scores)
        comp_res[name] = {"F1": f1, "Precision": prec, "Recall": rec, "FPR": fpr, "Esc_Recall": e_rec}

    # --- Behavioral Isolation ---
    behav_scores = [custom_fusion(0.0, x, 0.0, 1.0) for x in X_raw]
    behav_res = {}
    for t in [0.65, 0.35, 0.20, 0.10, 0.05]:
        auc, rec, prec, fpr, f1 = get_metrics(y_true, behav_scores, threshold=t)
        behav_res[str(t)] = {"Precision": prec, "Recall": rec, "F1": f1, "FPR": fpr}

    # --- Write paper_tables.md ---
    with open("paper_tables.md", "w") as f:
        f.write("# Research Results: Sentinel Prompt Injection Middleware\n\n")
        
        f.write("## 1. Primary Model Comparison\n")
        f.write("| Configuration | Overall F1 | Precision | Recall | FPR | Escalation Stress Test |\n")
        f.write("|---|---|---|---|---|---|\n")
        for k, v in comp_res.items():
            f.write(f"| {k} | {v['F1']:.4f} | {v['Precision']:.4f} | {v['Recall']:.4f} | {v['FPR']:.4f} | **{v['Esc_Recall']:.4f}** |\n")
            
        f.write("\n## 2. Behavioral Features Isolation (Threshold Analysis)\n")
        f.write("| Threshold | F1 | Precision | Recall | FPR |\n")
        f.write("|---|---|---|---|---|\n")
        for k, v in behav_res.items():
            f.write(f"| {k} | {v['F1']:.4f} | {v['Precision']:.4f} | {v['Recall']:.4f} | {v['FPR']:.4f} |\n")
            
        f.write("\n## 3. Logistic Regression Learned Coefficients\n")
        f.write("| Feature | Learned Weight |\n")
        f.write("|---|---|\n")
        for k, v in coef_res.items():
            f.write(f"| `{k}` | {v:.4f} |\n")
            
        f.write("\n## 4. Model Robustness (5-Fold Cross Validation Comparison)\n")
        f.write("| Metric | Nonlinear Gate (Mean ± Std) | Logistic Regression (Mean ± Std) |\n")
        f.write("|---|---|---|\n")
        f.write(f"| F1 Score | {cv_summary['Gate']['F1']} | {cv_summary['Logistic Regression']['F1']} |\n")
        f.write(f"| Precision | {cv_summary['Gate']['Precision']} | {cv_summary['Logistic Regression']['Precision']} |\n")
        f.write(f"| Recall | {cv_summary['Gate']['Recall']} | {cv_summary['Logistic Regression']['Recall']} |\n")
        f.write(f"| Escalation Recall | {cv_summary['Gate']['Escalation Recall']} | {cv_summary['Logistic Regression']['Escalation Recall']} |\n")
        
        f.write("\n## 5. Gate Threshold Sensitivity Grid\n")
        f.write("| Escalation Threshold | Topic Shift Threshold | Overall F1 | Escalation Recall |\n")
        f.write("|---|---|---|---|\n")
        for e in [0.7, 0.8, 0.9]:
            for t in [0.6, 0.7, 0.8]:
                scores_s = [custom_fusion(x["deberta_score"], x, 0.55, 0.45, e, t) for x in X_raw]
                preds_s = [1 if s >= 0.65 else 0 for s in scores_s]
                f1_s = f1_score(y_arr, preds_s, zero_division=0)
                e_scores_s = [scores_s[i] for i in esc_idx]
                e_p_s = [1 if s >= 0.65 else 0 for s in e_scores_s]
                esc_r_s = recall_score([y_true[i] for i in esc_idx], e_p_s, zero_division=0)
                f.write(f"| > {e} | > {t} | {f1_s:.4f} | {esc_r_s:.4f} |\n")

    print("Success: paper_tables.md and final_model_config.json updated.")

if __name__ == "__main__":
    run()
