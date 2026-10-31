import os
import time
 
from dotenv import load_dotenv
from google import genai
from google.genai import types
 
load_dotenv()
print("Key loaded:", bool(os.getenv("GEMINI_API_KEY")))
 
client = genai.Client(http_options=types.HttpOptions(timeout=20000))
 
print("Step 1: which flash models are available for this key?")
try:
    names = []
    for m in client.models.list():
        if "flash" in m.name:
            names.append(m.name)
    print("Flash models:", names)
except Exception as error:
    print("LIST ERROR:", type(error).__name__, error)
 
models_to_try = [os.getenv("LLM_MODEL", "gemini-flash-latest"), "gemini-flash-lite-latest"]
for model in models_to_try:
    print("Step 2: trying", model)
    start = time.time()
    try:
        response = client.models.generate_content(model=model, contents="Say hello in one short sentence.")
        print("OK:", response.text, f"({time.time() - start:.1f} s)")
    except Exception as error:
        print("ERROR:", type(error).__name__, error, f"({time.time() - start:.1f} s)")
 