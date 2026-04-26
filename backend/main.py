import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import logging

from pipeline import run_pipeline
from session.memory import get_stats, clear_session
from config import REDIS_HOST

# Models pre-loaded inherently through their module level initializations
from models.deberta_model import get_deberta_score
from models.minilm_model import get_embedding
from models.llm_model import generate_response
from attack_patterns import ATTACK_EMBEDDINGS
from behavioral.features import PROBING_EMBEDDINGS
from session.memory import r as redis_client

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

executor = ThreadPoolExecutor(max_workers=4)

class ChatRequest(BaseModel):
    session_id: str
    message: str = Field(..., max_length=2000)

@app.on_event("startup")
async def startup_event():
    logging.info("Starting up API...")
    try:
        redis_client.ping()
        logging.info("Connected to Redis successfully.")
    except Exception as e:
        logging.error(f"Failed to connect to Redis at {REDIS_HOST}: {e}")

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        executor, 
        run_pipeline, 
        req.session_id, 
        req.message
    )
    return result

@app.get("/api/stats")
async def stats_endpoint(session_id: str):
    return get_stats(session_id)

@app.delete("/api/session")
async def delete_session(session_id: str):
    clear_session(session_id)
    return {"ok": True}
