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


gemini_client = genai.Client(api_key=config.Gemini_api_key ) #gemini client for embedding

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
                    print(f"skipping the unsupported file {os.path.basename(path)}")
                    continue

                docs = loader.load()
                all_docs.extend(docs)
                print(f"The {os.path.basename(path)} is loaded successfully...")
            except Exception as e:
                print(f"Error loading the file {e}")
        else:
            print(f"file path not found!!!!: {path}")
    return all_docs




# --- -------------------------------------2. Chunks Splitter ---------------------------------------------------

def chunks_splitter(documents, chunk_size=3000, chunk_overlap=300):
    try:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        chunks = text_splitter.split_documents(documents)
        print(f"The chunks created succesfully and the number of chunks is {len(chunks)}")
        return chunks
    except Exception as e:
        print(f"Error splitting the documents {e}")
        return []




# ----------------------------------------------------- 3. RagPipeline Class -------------------------------------------
class RagPipeline:
    def __init__(self,):
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
            print("Qdrant Cloud collection created successfully!")
        else:
            print("Connected to existing Qdrant Cloud collection!")
        
        self.all_documents = []
        self.bm25 = None
        self._load_existing_documents_for_bm25()

    #--------------------------------------------- Loading existing docs --------------------------------------

    def _load_existing_documents_for_bm25(self):
        try:
            records, _ = self.qdrant.scroll(
                collection_name=self.collection_name,
                with_payload=True,
                with_vectors=False,  
                limit=10000
            )
            if records:
                self.all_documents = [record.payload.get("page_content", "") for record in records if record.payload]
                tokenized_docs = [doc.lower().split() for doc in self.all_documents]
                self.bm25 = BM25Okapi(tokenized_docs) if tokenized_docs else None
                print(f"BM25 initialized with {len(self.all_documents)} documents from cloud.")
        except Exception as e:
            print(f"Error loading documents for BM25: {e}")

    #------------------------------------------ Adding Documenst to cloud database -------------------------------------
        
    def add_documents(self, chunks):
        points = []
        for i, chunk in enumerate(chunks):
            try:
                text = chunk.page_content
                meta = chunk.metadata if isinstance(chunk.metadata, dict) else {"metadata": str(chunk.metadata)}
                meta["page_content"] = text  
                
                result = gemini_client.models.embed_content(
                    model=config.Embedding_model,
                    contents=text,
                    config={'output_dimensionality': 768}
                )
                vector = result.embeddings[0].values  
                
                point_id = str(uuid.uuid4())
                self.all_documents.append(text)

                points.append(PointStruct(id=point_id, vector=vector, payload=meta))
                print(f"Embedded chunk {i+1}/{len(chunks)}")
                success = True
                time.sleep(4)
            except Exception as e:
                if "429" in str(e):
                    print(f"Rate limit hit at chunk {i+1}. Sleeping for 50 seconds to reset quota...")
                    time.sleep(50)  
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

        
            tokenized_docs = [doc.lower().split() for doc in self.all_documents]
            self.bm25 = BM25Okapi(tokenized_docs)
            print("All data successfully added to Qdrant Cloud in batches!")
    # --------------------------------------- semantic search --------------------------------------

    def get_relevant_documents(self, query, top_k=3):
        try:
            
            result = gemini_client.models.embed_content(
                model= config.Embedding_model,
                contents=query,
                config={'output_dimensionality': 768}
            )
            query_vector = result.embeddings[0].values

           
            search_results = self.qdrant.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                limit=top_k
            )

            docs = [hit.payload.get("page_content") for hit in search_results.points if hit.payload and "page_content" in hit.payload]
            return docs
        except Exception as e:
            print(f"Error in vector search: {e}")
            return []

    #----------------------------------------- hybrid search ----------------------------------------

    def hybrid_search(self, query, top_k=3):
        try:
            # 1. Vector Search
            vector_docs = self.get_relevant_documents(query, top_k=top_k)

            # 2. BM25 Search
            bm25_docs = []
            if self.bm25 and self.all_documents:
                tokenized_query = query.lower().split()
                scores = self.bm25.get_scores(tokenized_query)
                top_indices = np.argsort(scores)[::-1][:top_k]
                bm25_docs = [self.all_documents[i] for i in top_indices if scores[i] > 0]

            # 3. RRF (Reciprocal Rank Fusion) - Lightweight ranking combination
            fusion_scores = {}
            k = 60

            for rank, doc in enumerate(vector_docs):
                if doc not in fusion_scores:
                    fusion_scores[doc] = 0.0
                fusion_scores[doc] += 1.0 / (k + rank + 1)

            for rank, doc in enumerate(bm25_docs):
                if doc not in fusion_scores:
                    fusion_scores[doc] = 0.0
                fusion_scores[doc] += 1.0 / (k + rank + 1)

            sorted_docs = sorted(fusion_scores.items(), key=lambda x: x[1], reverse=True)
            final_docs = [doc for doc, score in sorted_docs]

            if not final_docs:
                return vector_docs

            return final_docs[:top_k]

        except Exception as e:
            print(f"Error in hybrid search: {e}")
            return self.get_relevant_documents(query, top_k=top_k)

