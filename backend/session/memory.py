import redis
import fakeredis
import json
import numpy as np
from typing import List, Dict, Any
from config import REDIS_HOST, REDIS_PORT, REDIS_DB, SESSION_TTL_SECONDS

# Use fakeredis for local development/memory-only if REDIS_HOST is default
r = fakeredis.FakeRedis(decode_responses=True)

def get_history(session_id: str, include_embeddings: bool = False) -> List[Dict[str, Any]]:
    """
    Fetches session history. 
    By default, excludes large embeddings for performance (hot path).
    """
    key = f"session:{session_id}:turns"
    turns_raw = r.lrange(key, 0, -1)
    history = []
    
    for idx, turn_str in enumerate(turns_raw):
        turn = json.loads(turn_str)
        if include_embeddings:
            emb_key = f"session:{session_id}:emb:{idx}"
            emb_raw = r.get(emb_key)
            if emb_raw:
                turn["embedding"] = np.array(json.loads(emb_raw))
        history.append(turn)
    return history

def add_turn(session_id: str, turn_dict: Dict[str, Any]):
    """
    Saves a turn. Metadata (text, scores) goes to the main list.
    Heavy embeddings are offloaded to separate keys.
    """
    key = f"session:{session_id}:turns"
    turn_idx = r.llen(key)
    
    to_store = turn_dict.copy()
    embedding = to_store.pop("embedding", None)
    
    # Store Lite metadata
    r.rpush(key, json.dumps(to_store))
    r.expire(key, SESSION_TTL_SECONDS)
    
    # Store Heavy embedding separately
    if embedding is not None:
        emb_key = f"session:{session_id}:emb:{turn_idx}"
        if isinstance(embedding, np.ndarray):
            embedding = embedding.tolist()
        r.set(emb_key, json.dumps(embedding))
        r.expire(emb_key, SESSION_TTL_SECONDS)

def get_prev_risk(session_id: str) -> float:
    key = f"session:{session_id}:prev_risk"
    val = r.get(key)
    return float(val) if val is not None else 0.0

def set_prev_risk(session_id: str, risk_score: float):
    key = f"session:{session_id}:prev_risk"
    r.set(key, str(risk_score))
    r.expire(key, SESSION_TTL_SECONDS)

def update_stats(session_id: str, decision: str, risk_score: float, latency_ms: int):
    key = f"session:{session_id}:stats"
    r.hincrby(key, "total_turns", 1)
    r.hincrbyfloat(key, "total_risk", risk_score)
    r.hincrbyfloat(key, "total_latency_ms", float(latency_ms))
    
    if decision in ["WARN", "BLOCK"]:
        r.hincrby(key, "flagged", 1)
    if decision == "BLOCK":
        r.hincrby(key, "blocked", 1)
        
    r.expire(key, SESSION_TTL_SECONDS)

def get_stats(session_id: str) -> Dict[str, Any]:
    key = f"session:{session_id}:stats"
    stats = r.hgetall(key)
    if not stats:
        return {
            "total_turns": 0, "flagged": 0, "blocked": 0,
            "avg_risk": 0.0, "avg_latency_ms": 0.0
        }
    
    total_turns = int(stats.get("total_turns", 0))
    flagged = int(stats.get("flagged", 0))
    blocked = int(stats.get("blocked", 0))
    total_risk = float(stats.get("total_risk", 0.0))
    total_latency_ms = float(stats.get("total_latency_ms", 0.0))
    
    avg_risk = total_risk / total_turns if total_turns > 0 else 0.0
    avg_latency_ms = total_latency_ms / total_turns if total_turns > 0 else 0.0
    
    return {
        "total_turns": total_turns,
        "flagged": flagged,
        "blocked": blocked,
        "avg_risk": round(avg_risk, 4),
        "avg_latency_ms": round(avg_latency_ms, 2)
    }

def clear_session(session_id: str):
    r.delete(f"session:{session_id}:turns")
    r.delete(f"session:{session_id}:prev_risk")
    r.delete(f"session:{session_id}:stats")
    # Clean up embeddings (up to a reasonable count)
    for i in range(100):
        r.delete(f"session:{session_id}:emb:{i}")
