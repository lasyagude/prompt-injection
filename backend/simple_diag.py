import sys
print("START")
try:
    import torch
    print(f"TORCH OK: {torch.__version__}")
    from transformers import pipeline
    print("TRANSFORMERS OK")
    pipe = pipeline("text-generation", model="distilgpt2", device_map="cpu")
    print("PIPELINE OK")
    out = pipe("Hello", max_new_tokens=5)
    print(f"RESULT: {out}")
except Exception as e:
    print(f"ERROR: {e}")
print("FINISH")
