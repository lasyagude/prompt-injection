import logging
import threading
from transformers import pipeline

logger = logging.getLogger(__name__)

classifier = None
_load_event = threading.Event()

def _load_pipeline():
    global classifier
    logger.info("Initializing DeBERTa pipeline in background...")
    try:
        classifier = pipeline(
            "text-classification",
            model="ProtectAI/deberta-v3-base-prompt-injection-v2"
        )
        logger.info("DeBERTa pipeline initialized successfully!")
    except Exception as e:
        logger.error(f"Failed to load DeBERTa pipeline: {e}")
    finally:
        _load_event.set()

# Spawn background thread to load model, preventing import blocking
threading.Thread(target=_load_pipeline, daemon=True).start()

def get_deberta_score(text: str) -> float:
    if not _load_event.is_set():
        logger.warning("DeBERTa pipeline is still loading. Blocking request until ready...")
        _load_event.wait()

    if classifier is None:
        return 0.0
        
    try:
        # top_k=None returns scores for ALL classes, not just top-1.
        # This ensures we never silently return 0.0 when INJECTION is runner-up.
        results = classifier(text, truncation=True, max_length=512, top_k=None)
        
        logger.debug(f"DeBERTa raw results: {results}")

        # results is a list of lists when top_k=None: [[{'label':..,'score':..}, ...]]
        # Flatten if nested
        if results and isinstance(results[0], list):
            results = results[0]

        if not results:
            return 0.0

        # Directly find the INJECTION class score by label name
        for r in results:
            label = str(r.get('label', '')).upper()
            score = float(r.get('score', 0.0))
            if "INJECTION" in label or label == "LABEL_1":
                return round(score, 4)

        # Fallback: return 0.0 if INJECTION label not found at all
        return 0.0

    except Exception as e:
        logger.error(f"Error during DeBERTa inference: {e}")
        return 0.0

