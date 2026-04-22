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
        # Get scores for all classes
        results = classifier(text, truncation=True, max_length=512)
        
        # Log the raw output if it feels stuck at 0
        logger.debug(f"DeBERTa raw results: {results}")

        # The pipeline typically returns a list of dicts for single input
        # results: [{'label': 'INJECTION', 'score': 0.99}]
        if not results:
            return 0.0
            
        # Case-insensitive check for label containing "INJECTION"
        # Also handle standard binary labels like "LABEL_1" which is often used for injection in this model
        for r in results:
            label = str(r.get('label', '')).upper()
            score = float(r.get('score', 0.0))
            
            if "INJECTION" in label or label == "LABEL_1":
                return round(score, 4)
                
        # If we reach here and it's a binary classifier but we didn't find "INJECTION",
        # and the label is anything other than "SAFE" or "LABEL_0", it might be the target.
        # But safest is to return the score of the highest probability label if it's not "SAFE"
        top_result = results[0]
        if "SAFE" not in str(top_result.get('label', '')).upper() and "LABEL_0" not in str(top_result.get('label', '')).upper():
            return round(float(top_result.get('score', 0.0)), 4)

        return 0.0
    except Exception as e:
        logger.error(f"Error during DeBERTa inference: {e}")
        return 0.0
