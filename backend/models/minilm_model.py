from sentence_transformers import SentenceTransformer
import numpy as np
import logging
import threading
from config import MINILM_MODEL_ID

logger = logging.getLogger(__name__)

model = None
_load_event = threading.Event()

def _load_minilm():
    global model
    logger.info(f"Loading MiniLM model in background: {MINILM_MODEL_ID}")
    try:
        model = SentenceTransformer(MINILM_MODEL_ID)
        logger.info(f"MiniLM model loaded successfully!")
    except Exception as e:
        logger.error(f"Failed to load MiniLM {MINILM_MODEL_ID}: {e}")
    finally:
        _load_event.set()

threading.Thread(target=_load_minilm, daemon=True).start()

def get_embedding(text: str) -> np.ndarray:
    if not _load_event.is_set():
        logger.warning(f"MiniLM model {MINILM_MODEL_ID} is still loading. Blocking request until ready...")
        _load_event.wait()
        
    if model is None:
        return np.zeros((384,))
        
    return model.encode(text, normalize_embeddings=True)

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b))
