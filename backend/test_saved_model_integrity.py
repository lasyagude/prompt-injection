import sys
import traceback
from transformers import AutoConfig, AutoTokenizer, AutoModelForSequenceClassification
import torch

def test_load():
    model_path = r"c:\Users\Vasudha Pai\ui\backend\saved_model"
    print(f"Testing model loading from: {model_path}")
    
    try:
        print("1. Loading Config...")
        config = AutoConfig.from_pretrained(model_path)
        print("Config Loaded OK.")
        
        print("2. Loading Tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        print("Tokenizer Loaded OK.")
        
        print("3. Loading Model (this may take time/memory)...")
        # Load without weights for speed if we just want to check structure? 
        # No, let's load it fully to check integrity.
        model = AutoModelForSequenceClassification.from_pretrained(model_path)
        print("Model Loaded OK.")
        
        print("4. Testing Inference...")
        inputs = tokenizer("Hello world", return_tensors="pt")
        with torch.no_grad():
            outputs = model(**inputs)
        print("Inference Success. Results shape:", outputs.logits.shape)
        
        print("\nSUMMARY: The model appears to be correct and functional.")
        
    except Exception as e:
        print("\nFAILURE DETECTED:")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_load()
