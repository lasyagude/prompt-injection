import os

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

SESSION_TTL_SECONDS = 3600

LLM_MODEL_ID = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
MINILM_MODEL_ID = "all-MiniLM-L6-v2"
