import logging
import threading
from transformers import pipeline
from config import LLM_MODEL_ID

logger = logging.getLogger(__name__)

pipe = None
_load_event = threading.Event()

def _load_llm():
    global pipe
    logger.info(f"Loading LLM pipeline: {LLM_MODEL_ID}")
    try:
        # Use simple initializers to avoid external dependency issues (like accelerate)
        pipe = pipeline(
            "text-generation",
            model=LLM_MODEL_ID,
            device=-1 # Forced CPU
        )
        logger.info("LLM pipeline loaded successfully!")
    except Exception as e:
        print("ERROR LOADING MODEL:", e)   # 🔥 debug
        logger.error(f"Failed to load LLM {LLM_MODEL_ID}: {e}")
    finally:
        _load_event.set()

# Load in background
threading.Thread(target=_load_llm, daemon=True).start()

def generate_response(prompt: str) -> str:
    # Wait until model is ready
    if not _load_event.is_set():
        logger.warning("LLM still loading... waiting")
        _load_event.wait()

    if pipe is None:
        return "LLM failed to load."

    # Use a clear separator for the completion model
    safe_prompt = f"User: {prompt}\nAssistant:"

    output = pipe(
        safe_prompt,
        max_new_tokens=100,
        do_sample=True,
        temperature=0.7,
        return_full_text=False # Crucial: prevents prompt from appearing in the output
    )

    raw_response = output[0]["generated_text"].strip()
    
    # Prune hallucinated turns (User/Assistant loops)
    clean_response = raw_response.split("User:")[0].split("Assistant:")[0].strip()
    
    return clean_response if clean_response else "..."