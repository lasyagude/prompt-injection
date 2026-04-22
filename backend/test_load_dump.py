import sys, traceback
with open("c:/Users/Vasudha Pai/ui/backend/error_log.txt", "w") as f:
    f.write("Starting...\n")
    try:
        from transformers import pipeline
        f.write("Imported.\n")
        pipe = pipeline("text-generation", model="TinyLlama/TinyLlama-1.1B-Chat-v1.0", device_map="cpu")
        f.write("Loaded.\n")
    except Exception as e:
        f.write("Exception:\n")
        f.write(traceback.format_exc())
