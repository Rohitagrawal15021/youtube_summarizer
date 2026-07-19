import os
from dotenv import load_dotenv
from google import genai

# Load .env file
load_dotenv()

# Create Gemini client
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)