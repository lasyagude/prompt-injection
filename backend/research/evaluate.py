import json
import os
import sys
import uuid
import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score

# Add parent directory to path to import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline import run_pipeline
import pipeline
from session.memory import clear_session

# Mock LLM generation to massively speed up evaluation (we only care about risk scores)
pipeline.generate_response = lambda text: "Mocked LLM response"

DATA_FILE = os.path.join(os.path.dirname(__file__), "test_dataset.json")

def compute_metrics(y_true, y_scores, threshold=0.65):
    # Threshold at 0.65 for discrete metrics
    y_pred = [1 if s >= threshold else 0 for s in y_scores]
    
    # Continuous AUC over all thresholds
    try:
        auc = roc_auc_score(y_true, y_scores)
    except ValueError:
        auc = None # If only one class present
        
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    
    positives = sum(y_true)
    negatives = len(y_true) - positives
    
    tpr = sum((p == 1 and t == 1) for p, t in zip(y_pred, y_true)) / positives if positives > 0 else None
    fpr = sum((p == 1 and t == 0) for p, t in zip(y_pred, y_true)) / negatives if negatives > 0 else None

    return {
        "AUC": round(auc, 4) if auc is not None else "N/A",
        "Precision": round(prec, 4),
        "Recall (TPR)": round(tpr, 4) if tpr is not None else "N/A",
        "False Positive Rate (FPR)": round(fpr, 4) if fpr is not None else "N/A",
        "F1": round(f1, 4)
    }

def evaluate():
    with open(DATA_FILE, "r") as f:
        dataset = json.load(f)
        
    y_true_all = []
    scores_deberta = []
    scores_sentinel = []
    
    categories = {}
    
    print(f"Starting evaluation of {len(dataset)} examples...")
    for idx, ex in enumerate(dataset):
        # 1 for INJECTION, 0 for SAFE
        label = 1 if ex["label"] == "INJECTION" else 0
        cat = ex["category"]
        
        if cat not in categories:
            categories[cat] = {"y_true": [], "deberta": [], "sentinel": []}
            
        session_id = str(uuid.uuid4())
        clear_session(session_id)
        
        # Replay history to build up memory state
        if "history" in ex:
            for h in ex["history"]:
                if h["role"] == "user":
                    run_pipeline(session_id, h["text"])
                    
        # Evaluate final turn
        result = run_pipeline(session_id, ex["text"])
        
        deb_score = result["deberta_score"]
        risk_score = result["risk_score"]
        
        clear_session(session_id)
        
        y_true_all.append(label)
        scores_deberta.append(deb_score)
        scores_sentinel.append(risk_score)
        
        categories[cat]["y_true"].append(label)
        categories[cat]["deberta"].append(deb_score)
        categories[cat]["sentinel"].append(risk_score)
        
        # Simple progress bar
        print(f"Processed {idx+1}/{len(dataset)}...", end="\r")

    print("\n\n--- Overall Metrics ---")
    overall_deb = compute_metrics(y_true_all, scores_deberta)
    overall_sen = compute_metrics(y_true_all, scores_sentinel)
    
    results = {
        "overall": {
            "Baseline (DeBERTa)": overall_deb,
            "Sentinel (Full)": overall_sen
        },
        "per_category": {}
    }
    
    print("Baseline (DeBERTa):")
    for k, v in overall_deb.items(): print(f"  {k}: {v}")
    print("Sentinel (Full):")
    for k, v in overall_sen.items(): print(f"  {k}: {v}")
    
    print("\n--- Per-Category Metrics ---")
    for cat, data in categories.items():
        met_deb = compute_metrics(data["y_true"], data["deberta"])
        met_sen = compute_metrics(data["y_true"], data["sentinel"])
            
        results["per_category"][cat] = {
            "Baseline (DeBERTa)": met_deb,
            "Sentinel (Full)": met_sen
        }
        print(f"\n[{cat.upper()}]")
        print("  Baseline (DeBERTa):")
        for k, v in met_deb.items(): print(f"    {k}: {v}")
        print("  Sentinel (Full):")
        for k, v in met_sen.items(): print(f"    {k}: {v}")
        
    out_path = os.path.join(os.path.dirname(__file__), 'eval_results.json')
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved detailed results to {out_path}")

if __name__ == "__main__":
    evaluate()
