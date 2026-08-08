import os 
from dotenv import load_dotenv
load_dotenv()

Groq_api_key = os.getenv("GROQ_API_KEY")

file_path = ["./data/diabetes.pdf","./data/hypertension.pdf"]

Groq_model = "llama-3.3-70b-versatile"

database_path = './chroma_db'

Embedding_model = "all-MiniLM-L6-v2"