# MediPulse AI | Clinical Intelligence Assistant

> **Live Application Link:**: https://diabetesbpairagpipeline-yw5tb8cd6szoyktzqbi2mn.streamlit.app/

## 🚀 Overview
**MediPulse AI** is a specialized, production-ready RAG (Retrieval-Augmented Generation) web application designed to act as an elite medical clinical assistant. It focuses exclusively on **Diabetes** and **Blood Pressure (Hypertension/Hypotension)** management, utilizing advanced hybrid search, strict domain guardrails, and real-time streaming responses.

---

## 🛠 Key Features
* **Hybrid Search Engine:** Combines Qdrant Cloud vector search (via Google Gemini embeddings) with BM25 keyword scoring, optimized by Reciprocal Rank Fusion (RRF) for high-precision retrieval.
* **Domain Guardrails:** Implements strict logical boundaries; enforces a zero-tolerance policy for out-of-scope queries (e.g., general lifestyle or personal scheduling) with automated professional refusals.
* **Language & Hinglish Support:** Detects user input script, maintaining continuity for English, Devanagari, and Romanized Hinglish.
* **Streaming Architecture:** Leverages FastAPI and LangChain for token-by-token streaming, providing a fast, responsive chat interface.
* **Containerized Deployment:** Fully Dockerized microservices architecture with `docker-compose` orchestration.

---

## 💻 Tech Stack
* **Frameworks:** FastAPI (Backend), Streamlit (Frontend)
* **LLM & AI:** Groq (`llama-3.3-70b-versatile`), LangChain, Google GenAI SDK
* **Vector DB:** Qdrant Cloud
* **Libraries:** `rank-bm25`, `numpy`, `langchain-core`, `langchain-groq`, `langchain-community`, `pydantic`
* **Infrastructure:** Docker, Docker Compose

---

## 📂 Project Structure
* `backend.py`: Core FastAPI logic, system prompt orchestration, and dynamic data ingestion.
* `frontend.py`: Custom-styled Streamlit interface with a "Linear-inspired" dark aesthetic.
* `rag_core.py`: Implementation of RAG pipeline, document processing, and vector database management.
* `config.py`: Centralized management for environment variables and API models.
* `docker-compose.yml`: Multi-container orchestration instructions.
* `Dockerfile.backend` / `Dockerfile.frontend`: Container configuration files.
* `requirements.txt`: Project dependency manifest.

---

## ⚠️ Important Note
* This repository requires a `.env` file containing your `GROQ_API_KEY`, `GEMINI_API_KEY`, `QDRANT_URL`, and `QDRANT_API_KEY`.
* Ensure local storage requirements (data files, caches) are maintained as per the system architecture.
