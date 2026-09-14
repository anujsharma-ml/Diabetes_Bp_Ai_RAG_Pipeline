# rag_core.py
import os
import config
import uuid
import time
import numpy as np
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from google import genai  
from qdrant_client import QdrantClient  
from qdrant_client.http.models import Distance, VectorParams, PointStruct  
from rank_bm25 import BM25Okapi  
from flashrank import Ranker, RerankRequest

# Initialize Gemini Client for Embeddings
gemini_client = genai.Client(api_key=config.Gemini_api_key)

# ------------------------------------------ 1. File Loader -----------------------------------------------
def file_loader(files):
    all_docs = []
    for path in files:
        if os.path.exists(path):
            try:
                if path.endswith(".pdf"):
                    loader = PyPDFLoader(path)
                elif path.endswith(".docx") or path.endswith(".doc"):
                    loader = Docx2txtLoader(path)
                elif path.endswith(".txt"):
                    loader = TextLoader(path)
                else:
                    print(f"Skipping unsupported file: {os.path.basename(path)}")
                    continue

                docs = loader.load()
                all_docs.extend(docs)
                print(f"Successfully loaded {os.path.basename(path)}...")
            except Exception as e:
                print(f"Error loading file {path}: {e}")
        else:
            print(f"File path not found: {path}")
    return all_docs


# ------------------------------------------ 2. Chunks Splitter -------------------------------------------
def chunks_splitter(documents, chunk_size=3000, chunk_overlap=300):
    try:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        chunks = text_splitter.split_documents(documents)
        print(f"Chunks created successfully! Total chunks: {len(chunks)}")
        return chunks
    except Exception as e:
        print(f"Error splitting documents: {e}")
        return []


# ------------------------------------------ 3. RagPipeline Class -----------------------------------------
class RagPipeline:
    def __init__(self):
        self.qdrant = QdrantClient(
            url=config.Qdrant_url,
            api_key=config.Qdrant_api_key
        )
        self.collection_name = "medipulse_docs"

        if not self.qdrant.collection_exists(self.collection_name):
            self.qdrant.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=768, distance=Distance.COSINE),
            )
            print("Created new Qdrant Cloud collection!")
        else:
            print("Connected to existing Qdrant Cloud collection!")
        
        # CPU-Optimized Ultra Light Cross-Encoder Reranker
        print("Initializing FlashRank Reranker...")
        self.reranker = Ranker(model_name="ms-marco-TinyBERT-L-2-v2")

    # ------------------------------------------ Add Documents to Vector DB --------------------------------
    def add_documents(self, chunks):
        points = []
        for i, chunk in enumerate(chunks):
            try:
                text = chunk.page_content
                meta = chunk.metadata if isinstance(chunk.metadata, dict) else {"metadata": str(chunk.metadata)}
                meta["page_content"] = text  
                meta["source"] = meta.get("source", "unknown")
                
                result = gemini_client.models.embed_content(
                    model=config.Embedding_model,
                    contents=text,
                    config={'output_dimensionality': 768}
                )
                vector = result.embeddings[0].values  
                
                point_id = str(uuid.uuid4())
                points.append(PointStruct(id=point_id, vector=vector, payload=meta))
                print(f"Embedded chunk {i+1}/{len(chunks)}")
                time.sleep(3)
            except Exception as e:
                if "429" in str(e):
                    print(f"Rate limit hit at chunk {i+1}. Sleeping for 30 seconds...")
                    time.sleep(30)
                else:
                    print(f"Error processing chunk {i}: {e}")
                    break

        if points:
            batch_size = 50
            for i in range(0, len(points), batch_size):
                batch = points[i:i + batch_size]
                try:
                    self.qdrant.upsert(
                        collection_name=self.collection_name,
                        points=batch
                    )
                    print(f"Uploaded batch {i // batch_size + 1} successfully!")
                except Exception as e:
                    print(f"Error uploading batch {i // batch_size + 1}: {e}")

    # ------------------------------------------ Dense Vector Search ---------------------------------------
    def get_relevant_documents(self, query, top_k=10):
        try:
            result = gemini_client.models.embed_content(
                model=config.Embedding_model,
                contents=query,
                config={'output_dimensionality': 768}
            )
            query_vector = result.embeddings[0].values

            search_results = self.qdrant.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                limit=top_k
            )

            docs = [
                hit.payload.get("page_content") 
                for hit in search_results.points 
                if hit.payload and "page_content" in hit.payload
            ]
            return docs
        except Exception as e:
            print(f"Error in vector search: {e}")
            return []

    # ------------------------------------------ Cross-Encoder Reranking -----------------------------------
    def rerank_documents(self, query: str, docs: list[str], top_n: int = 3) -> list[str]:
        if not docs:
            return []
        try:
            passages = [{"id": idx, "text": doc} for idx, doc in enumerate(docs)]
            rerank_req = RerankRequest(query=query, passages=passages)
            results = self.reranker.rerank(rerank_req)
            
            # Extract top N ranked texts after re-scoring
            reranked_docs = [res["text"] for res in results[:top_n]]
            return reranked_docs
        except Exception as e:
            print(f"Error in Reranking: {e}")
            return docs[:top_n]

    # ------------------------------------------ Hybrid Retrieval + Rerank Pipeline ------------------------
    def hybrid_search(self, query, top_k=3):
        try:
            # 1. Candidate Retrieval: Fetch top 10 relevant documents from Qdrant Cloud
            candidate_docs = self.get_relevant_documents(query, top_k=10)

            if not candidate_docs:
                return []

            # 2. Re-Ranking Phase: Pass candidates through FlashRank Reranker to get top 3 best matching docs
            final_docs = self.rerank_documents(query, candidate_docs, top_n=top_k)
            return final_docs

        except Exception as e:
            print(f"Error in hybrid search pipeline: {e}")
            return self.get_relevant_documents(query, top_k=top_k) 