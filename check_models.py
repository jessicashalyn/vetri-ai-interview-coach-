import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ GEMINI_API_KEY not found in .env file!")
    print("Please add your API key to .env file")
    exit()

print("✅ API Key found. Configuring...")
genai.configure(api_key=api_key)

print("\n📋 Available models:")
print("=" * 50)

for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"  ✅ {model.name}")

print("=" * 50)
print("\n💡 Use one of the above model names in your code.")