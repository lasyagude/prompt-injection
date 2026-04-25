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
        pipe = pipeline(
            "text-generation",
            model=LLM_MODEL_ID,
            device=-1  # Forced CPU
        )
        logger.info("LLM pipeline loaded successfully!")
    except Exception as e:
        print("ERROR LOADING MODEL:", e)
        logger.error(f"Failed to load LLM {LLM_MODEL_ID}: {e}")
    finally:
        _load_event.set()

# Load in background
threading.Thread(target=_load_llm, daemon=True).start()

# TinyLlama uses ChatML format — this is the correct prompt template
SYSTEM_PROMPT = (
    "You are a concise assistant. "
    "Reply in 1-2 short sentences only. "
    "Do not explain, do not use bullet points, do not elaborate."
)

def _build_chatml_prompt(user_message: str) -> str:
    return (
        f"<|system|>\n{SYSTEM_PROMPT}</s>\n"
        f"<|user|>\n{user_message}</s>\n"
        f"<|assistant|>\n"
    )

def generate_response(prompt: str) -> str:
    if not _load_event.is_set():
        logger.warning("LLM still loading... waiting")
        _load_event.wait()

    if pipe is None:
        return "LLM failed to load."

    chatml_prompt = _build_chatml_prompt(prompt)

    output = pipe(
        chatml_prompt,
        max_new_tokens=60,             # Hard cap — forces short replies
        do_sample=False,               # Greedy decoding: faster, no sampling overhead
        repetition_penalty=1.1,
        return_full_text=False
    )

    raw = output[0]["generated_text"].strip()

    # Strip any leaked ChatML tokens if model repeats them
    for stop_token in ["</s>", "<|user|>", "<|system|>", "<|assistant|>"]:
        raw = raw.split(stop_token)[0].strip()

    return raw if raw else "I'm not sure how to respond to that."