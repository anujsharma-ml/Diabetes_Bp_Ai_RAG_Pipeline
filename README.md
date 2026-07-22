# 🩺 Medical Assistant RAG Chatbot (Diabetes & BP Support)

A specialized, context-aware Retrieval-Augmented Generation (RAG) chatbot built to answer medical queries strictly from authorized documents. It focuses exclusively on **Diabetes and Hypertension (Blood Pressure)** to prevent LLM hallucinations and provide accurate, source-backed responses.

---

## 💡 Ownership & Transparency
* **🧠 RAG Pipeline & Core Logic (100% Built By Me):** 
  The entire brain and intelligence of this application—including document ingestion, text splitting strategies, vector embeddings configuration, local vector database (`ChromaDB`) management, and context-retrieval mechanisms—is completely designed, written, and implemented by me.
* **🌐 FastAPI Backend & Streamlit Frontend (Built with AI Assistance):** 
  The wrapper infrastructure layers (FastAPI server endpoints, Pydantic request models, response streaming, and Streamlit UI) were constructed using AI as a development assistant based on my project flow requirements.

---

## ⚙️ What This Project Does (Core Capabilities)

1. **Strict Context-Bound Answers:** 
   Unlike normal ChatGPT which uses external/general knowledge, this chatbot only answers using the provided PDF documents. If the question is outside Diabetes or BP, it safely refuses to answer.
2. **Document Processing & Chunking:** 
   Takes medical PDF documents, breaks them down into optimal text chunks using LangChain text splitters for better semantic search.
3. **Local Vector Embeddings & Storage:** 
   Converts text chunks into dense mathematical vector representations using `SentenceTransformers` and stores them securely in a local persistent `ChromaDB` database.
4. **Relevant Information Retrieval:** 
   When a user asks a question, it queries ChromaDB to instantly pull the top most relevant context chunks.
5. **Real-Time Token Streaming:** 
   Powered by the `Groq LLM` API, responses stream back chunk-by-chunk (just like ChatGPT) via a FastAPI backend to a clean Streamlit chat interface.

---

## 🛠️ Tech Stack
* **Language:** Python
* **RAG & AI Core:** LangChain, SentenceTransformers, ChromaDB, Groq LLM (Llama/Mixtral)
* **Backend:** FastAPI, Uvicorn, Pydantic
* **Frontend:** Streamlit, Requests

---

## 📂 Project Structure
```text
├── rag_core.py         # 🧠 My custom-built RAG pipeline, loader, and ChromaDB logic
├── backend.py          # FastAPI server, request validation, and LLM streaming endpoint
├── frontend.py         # Streamlit interactive chat UI
├── config.py           # Configuration variables and API keys (Ignored in Git)
├── requirements.txt    # Required Python libraries list
└── README.md           # Project documentation