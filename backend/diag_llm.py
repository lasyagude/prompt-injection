import sys
import os
import torch
import logging
import traceback
from transformers import pipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Diagnostics")

MODEL_ID = "distilgpt2"

def run_diagnostics():
    logger.info(f"--- STARTING LLM DIAGNOSTICS ---")
    logger.info(f"Model ID: {MODEL_ID}")
    logger.info(f"Python Version: {sys.version}")
    logger.info(f"PyTorch Version: {torch.__version__}")
    logger.info(f"CUDA Available: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available():
        logger.info(f"CUDA Device: {torch.cuda.get_device_name(0)}")
    
    try:
        import accelerate
        logger.info(f"Accelerate Version: {accelerate.__version__}")
    except ImportError:
        logger.error("ACCELERATE NOT INSTALLED")

    logger.info("Attempting to load pipeline with device_map='cpu'...")
    try:
        pipe = pipeline(
            "text-generation",
            model=MODEL_ID,
            device_map="cpu",
            trust_remote_code=True
        )
        logger.info("Pipeline loaded successfully on CPU!")
        
        test_prompt = "User: Hello\nAssistant:"
        logger.info(f"Running test inference with prompt: {test_prompt}")
        output = pipe(test_prompt, max_new_tokens=20)
        logger.info(f"Output: {output}")
        
    except Exception as e:
        logger.error("FAILED TO LOAD PIPELINE")
        traceback.print_exc()

if __name__ == "__main__":
    run_diagnostics()
