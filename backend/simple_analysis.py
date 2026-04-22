import os
import json

def analyze_files():
    path = r"c:\Users\Vasudha Pai\ui\backend\saved_model"
    print(f"Analyzing path: {path}")
    
    if not os.path.exists(path):
        print("ERROR: Path does not exist.")
        return
        
    files = os.listdir(path)
    print(f"Files found: {files}")
    
    # Check config.json
    if "config.json" in files:
        try:
            with open(os.path.join(path, "config.json"), 'r') as f:
                config = json.load(f)
                print("config.json: VALID JSON")
                print(f" - Model Type: {config.get('model_type')}")
                print(f" - Architecture: {config.get('architectures')}")
        except Exception as e:
            print(f"config.json: BROKEN - {e}")
    else:
        print("config.json: MISSING")
        
    # Check model weights
    if "model.safetensors" in files:
        size = os.path.getsize(os.path.join(path, "model.safetensors"))
        print(f"model.safetensors: FOUND ({size} bytes)")
    elif "pytorch_model.bin" in files:
         size = os.path.getsize(os.path.join(path, "pytorch_model.bin"))
         print(f"pytorch_model.bin: FOUND ({size} bytes)")
    else:
        print("Model weights: MISSING (neither .safetensors nor .bin found)")

    # Check tokenizer
    if "tokenizer.json" in files:
        print("tokenizer.json: FOUND")
    if "tokenizer_config.json" in files:
        print("tokenizer_config.json: FOUND")
    
    print("Basic file check complete.")

if __name__ == "__main__":
    analyze_files()
