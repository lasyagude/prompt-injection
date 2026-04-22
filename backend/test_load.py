import traceback
print("Starting script...")
try:
    from transformers import pipeline
    print("Transformers imported.")
    
    pipe = pipeline("text-generation", model="TinyLlama/TinyLlama-1.1B-Chat-v1.0", device_map="cpu")
    print("Pipeline loaded!")
except Exception as e:
    print("Caught exception:")
    traceback.print_exc()
print("Done.")
