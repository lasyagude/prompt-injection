import json
import os
import sys
import uuid

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline import run_pipeline
from session.memory import clear_session
import pipeline

# Mock LLM generation for speed
pipeline.generate_response = lambda text: "Mocked LLM response"

DATA_FILE = os.path.join(os.path.dirname(__file__), "test_dataset.json")

def find_misses():
    with open(DATA_FILE, "r") as f:
        dataset = json.load(f)
        
    print("Finding multi_turn_escalation examples where DeBERTa scores < 0.65...\n")
    
    misses = []
    
    for ex in dataset:
        if ex["category"] != "multi_turn_escalation":
            continue
            
        session_id = str(uuid.uuid4())
        clear_session(session_id)
        
        # Build history
        if "history" in ex:
            for h in ex["history"]:
                if h["role"] == "user":
                    run_pipeline(session_id, h["text"])
                    
        # Evaluate turn 3
        result = run_pipeline(session_id, ex["text"])
        deb_score = result["deberta_score"]
        
        if deb_score < 0.65:
            misses.append((ex, deb_score, result["features"]))
            
        clear_session(session_id)
        
    print(f"Found {len(misses)} examples out of 45 where DeBERTa alone fails to BLOCK:\n")
    
    for i, (ex, score, feats) in enumerate(misses, 1):
        print(f"--- Example {i} ---")
        for h in ex.get("history", []):
            print(f"  {h['role'].title()}: {h['text']}")
        print(f"  Current Turn (Attack): {ex['text']}")
        print(f"  > DeBERTa Score : {score}")
        print(f"  > Escalation Rate: {feats.get('escalation_rate', 0.0)}")
        print(f"  > Topic Shift    : {feats.get('conversation_trajectory', 0.0)}")
        print()

if __name__ == "__main__":
    find_misses()
