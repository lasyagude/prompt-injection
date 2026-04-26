import time
from concurrent.futures import ThreadPoolExecutor
from models.minilm_model import get_embedding
from models.deberta_model import get_deberta_score
from models.llm_model import generate_response
from session.memory import get_history, add_turn, get_prev_risk, set_prev_risk, update_stats
from behavioral.features import (
    attack_pattern_similarity,
    probing_similarity,
    role_shift_counter,
    conversation_trajectory,
    repetition_similarity,
    flag_rate,
    escalation_rate
)
from behavioral.risk import compute_risk

def run_pipeline(session_id: str, text: str) -> dict:
    start_time = time.time()
    
    # H5: Input Validation - prevent excessive lengths from causing OOM or silent truncation
    if len(text) > 2000:
        text = text[:2000]
    
    # H1: Parallelize MiniLM and DeBERTa inference for lower latency
    with ThreadPoolExecutor(max_workers=2) as executor:
        future_emb = executor.submit(get_embedding, text)
        future_deb = executor.submit(get_deberta_score, text)
        
        embedding = future_emb.result()
        deberta_score = future_deb.result()
    
    history = get_history(session_id, include_embeddings=True)
    
    features = {
        "attack_pattern_similarity": attack_pattern_similarity(embedding),
        "probing_similarity": probing_similarity(embedding),
        "role_shift_counter": role_shift_counter(text),
        "conversation_trajectory": conversation_trajectory(embedding, history),
        "repetition_similarity": repetition_similarity(embedding, history),
        "flag_rate": flag_rate(history)
    }

    prev_risk = get_prev_risk(session_id)
    history_risks = [item.get("risk_score", 0.0) for item in history]
    features["escalation_rate"] = escalation_rate(history_risks)
    
    risk_score, decision = compute_risk(
        deberta_score=deberta_score,
        role_shift=features["role_shift_counter"],
        topic_shift=features["conversation_trajectory"],
        attack_pattern=features["attack_pattern_similarity"],
        probing=features["probing_similarity"],
        repetition=features["repetition_similarity"],
        flag_rate=features["flag_rate"],
        escalation=features["escalation_rate"],
        prev_risk=prev_risk,
        history_risks=history_risks
    )
    
    if decision in ["ALLOW", "WARN"]:
        llm_response = generate_response(text)
    else:
        llm_response = None
        
    latency_ms = int((time.time() - start_time) * 1000)
    
    turn_data = {
        "text": text,
        "embedding": embedding,
        "deberta_score": deberta_score,
        "features": features,
        "risk_score": risk_score,
        "decision": decision,
        "latency_ms": latency_ms
    }
    
    add_turn(session_id, turn_data)
    set_prev_risk(session_id, risk_score)
    update_stats(session_id, decision, risk_score, latency_ms)
    
    return {
        "decision": decision,
        "risk_score": risk_score,
        "deberta_score": deberta_score,
        "features": features,
        "llm_response": llm_response,
        "latency_ms": latency_ms
    }
