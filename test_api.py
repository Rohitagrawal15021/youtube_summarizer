import os
from dotenv import load_dotenv
from google import genai

# Load .env file
load_dotenv()

# Create Gemini client
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# Generate response
response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents="my name is rohit kumar agrawal say hello to me and tell me abot ai " 
)

print(response.text)