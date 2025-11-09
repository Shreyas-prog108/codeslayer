import os
from dotenv import load_dotenv

load_dotenv()

# Gemini API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Legacy support
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
