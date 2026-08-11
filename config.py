import os 
from dotenv import load_dotenv
load_dotenv()

Groq_api_key = os.getenv("GROQ_API_KEY")
Qdrant_url = os.getenv("QDRANT_URL")
Qdrant_api_key = os.getenv("QDRANT_API_KEY")
Gemini_api_key = os.getenv("GEMINI_API_KEY")

file_path = ["./data/diabetes.pdf","./data/hypertension.pdf"]

Groq_model = "llama-3.1-8b-instant"

Embedding_model = "gemini-embedding-2"
