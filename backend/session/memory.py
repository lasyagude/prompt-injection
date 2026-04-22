import redis
import fakeredis
import json
import numpy as np
from typing import List, Dict, Any
from config import REDIS_HOST, REDIS_PORT, REDIS_DB, SESSION_TTL_SECONDS

r = fakeredis.FakeRedis(decode_responses=True)

def get_history(session_id: str) -> List[Dict[str, Any]]:
    key = f"session:{session_id}:turns"
    turns = r.lrange(key, 0, -1)
    history = []
    for turn_str in turns:
        turn = json.loads(turn_str)
        if "embedding" in turn:
            turn["embedding"] = np.array(turn["embedding"])
        history.append(turn)
    return history

def add_turn(session_id: str, turn_dict: Dict[str, Any]):
    key = f"session:{session_id}:turns"
    to_store = turn_dict.copy()
    if "embedding" in to_store and isinstance(to_store["embedding"], np.ndarray):
        to_store["embedding"] = to_store["embedding"].tolist()
    
    r.rpush(key, json.dumps(to_store))
    r.expire(key, SESSION_TTL_SECONDS)

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
            "total_turns": 0,
            "flagged": 0,
            "blocked": 0,
            "avg_risk": 0.0,
            "avg_latency_ms": 0.0
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
