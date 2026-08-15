import os 
from dotenv import load_dotenv
load_dotenv()

Qdrant_url = os.getenv("QDRANT_URL")
Qdrant_api_key = os.getenv("QDRANT_API_KEY")
Gemini_api_key = os.getenv("GEMINI_API_KEY")
Groq_api_key = os.getenv("GROQ_API_KEY")

file_path = ["./data/diabetes.pdf","./data/hypertension.pdf","./data/bp_treatment.pdf","./data/icmr_guidline.pdf"]

Groq_model = "openai/gpt-oss-120b"

Embedding_model = "gemini-embedding-2"
