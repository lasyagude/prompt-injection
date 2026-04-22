import os
import sys

try:
    import psutil
    mem = psutil.virtual_memory()
    print(f"Total: {mem.total / (1024**3):.2f} GB")
    print(f"Available: {mem.available / (1024**3):.2f} GB")
    print(f"Used: {mem.used / (1024**3):.2f} GB")
except ImportError:
    print("psutil not installed. Trying alternative...")
    # fallback for windows if psutil missing
    if sys.platform == "win32":
        os.system("systeminfo | findstr /C:\"Total Physical Memory\" /C:\"Available Physical Memory\"")
