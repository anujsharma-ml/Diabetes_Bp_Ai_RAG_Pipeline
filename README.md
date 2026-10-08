# MediPulse AI | Clinical Intelligence Assistant

> **Live Application Gateway:** [Launch MediPulse AI Web App](https://diabetesbpairagpipeline-egnh5crjjtbher5eczhmwx.streamlit.app/)

---

## 🚀 Overview
**MediPulse AI** is a specialized, production-ready RAG (Retrieval-Augmented Generation) clinical assistant web application designed to deliver instant, evidence-based insights for **Diabetes** and **Blood Pressure (Hypertension/Hypotension)** management. Built using a decoupled microservices architecture, it integrates high-precision retrieval mechanisms with strict domain-guardrail system prompting.

---

## 🛠 Architectural Upgrades & Problem Solutions (Before vs. After)

### 1. Retrieval Engine Evolution
* **Before (RAM Bottleneck & Low Precision):** Loaded an in-memory `BM25Okapi` sparse retriever on server boot alongside dense vector search[cite: 9, 13, 27]. This caused exponential RAM consumption and memory leaks as document chunks grew[cite: 9, 13, 27].
* **After (Two-Stage Cross-Encoder Pipeline):** Replaced in-memory BM25 with a **Two-Stage Retrieval Engine**[cite: 27]:
  * **Stage 1 (Bi-Encoder Retrieval):** Fetches Top 10 broad candidate chunks from **Qdrant Cloud** using Google Gemini Embeddings (`gemini-embedding-2`)[cite: 27].
  * **Stage 2 (Cross-Encoder Re-Ranking):** Evaluates candidate chunks through a local CPU-optimized **FlashRank Reranker** (`ms-marco-TinyBERT-L-2-v2`), extracting the Top 3 highest-precision medical passages for LLM inference[cite: 27].

### 2. High-Concurrency & Event Loop Optimization
* **Before (Event Loop Blocking):** Synchronous vector queries and CPU-heavy FlashRank scoring ran directly inside FastAPI's async event loop[cite: 19, 27], causing server freezes when multiple users sent queries simultaneously.
* **After (Threadpool Offloading):** Offloaded synchronous heavy tasks using FastAPI's `run_in_threadpool`[cite: 19], isolating computational blocking to worker threads while keeping the main async event loop lightweight and non-blocking (`llm.astream`)[cite: 19].

### 3. Container Cold-Start & Deployment Stability
* **Before (Startup Timeout):** Executed automatic ingestion and PDF processing on backend boot[cite: 4, 19], causing cloud hosting platforms (like Render) to hit 50-second health-check timeouts[cite: 4, 19].
* **After (Decoupled Ingestion Pipeline):** Separated data ingestion into a standalone `ingest.py` script[cite: 25]. The backend API boots instantly (in ~2 seconds) without touching raw PDFs[cite: 19, 25].

---

## 💻 Tech Stack
* **Frameworks:** FastAPI (Backend Microservice), Streamlit (Custom Glassmorphic Frontend)[cite: 19, 24]
* **LLM Orchestration:** LangChain, Groq API (`llama-3.3-70b-versatile`)[cite: 19, 20]
* **Vector DB & Embeddings:** Qdrant Cloud, Google GenAI SDK (`gemini-embedding-2`)[cite: 20, 27]
* **Precision Scoring:** FlashRank Cross-Encoder (`ms-marco-TinyBERT-L-2-v2`)[cite: 27, 29]
* **Containerization:** Docker, Docker Compose[cite: 21, 22, 23]

---

## 📂 Project Structure
```text
.
├── backend.py            # Async FastAPI app with threadpool offloading & SSE streaming
├── frontend.py           # Custom Streamlit interface with chat history state & controls
├── rag_core.py           # 2-Stage Retrieval pipeline (Qdrant + FlashRank Reranker)
├── prompt.py             # System prompt template with multi-language & domain guardrails
├── styles.py             # Matte Obsidian theme CSS & visual animations
├── ingest.py             # Decoupled PDF loader, splitter, embedding & upsert script
├── config.py             # Environment configuration & model declarations
├── Dockerfile.backend    # Container definition for FastAPI service
├── Dockerfile.frontend   # Container definition for Streamlit UI
├── docker-compose.yml    # Multi-container local orchestration script
├── requirements.txt      # Production Python dependencies manifest
└── data/                 # Medical domain PDFs (Diabetes, Hypertension, ICMR Guidelines)
