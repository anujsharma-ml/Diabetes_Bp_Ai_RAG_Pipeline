import os
import numpy as np
import chromadb
import uuid
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer,CrossEncoder
import config
from rank_bm25 import BM25Okapi

# --- 1. File Loader ---
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




# --- 2. Chunks Splitter ---
def chunks_splitter(documents, chunk_size=1000, chunk_overlap=200):
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




# --- 3. RagPipeline Class ---
class RagPipeline:
    def __init__(self, drive_path=config.database_path):
        self.client = chromadb.PersistentClient(path=drive_path)
        self.collection = self.client.get_or_create_collection(name="collection")
        self.embedding_model = SentenceTransformer(config.Embedding_model)


        all_data = self.collection.get(include=['documents'])
        self.all_documents = all_data['documents'] if all_data['documents'] else []
        tokenized_docs = [doc.lower().split() for doc in self.all_documents]
        self.bm25 = BM25Okapi(tokenized_docs) if tokenized_docs else None
        
        
        self.reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

    def add_documents(self, chunks):
        ids = []
        embeddings = []
        documents = []
        metadatas = []

        for i, chunk in enumerate(chunks):
            try:
                text = chunk.page_content
                meta = chunk.metadata if isinstance(chunk.metadata, dict) else {"metadata": str(chunk.metadata)}
                ids.append(str(uuid.uuid4()))
                embeddings.append(self.embedding_model.encode(text).tolist())
                documents.append(text)
                metadatas.append(meta)
            except Exception as e:
                print(f"document add error: {e} on position {i}")

        try:
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )
            print("Data successfully added to ChromaDB collection!!!")
        except Exception as e:
            print(f"Adding data to collection error: {e}")



    def get_relevant_documents(self, query, top_k=3):
        try:
            query_vector = self.embedding_model.encode(query).tolist()
            results = self.collection.query(
                query_embeddings=[query_vector],
                n_results=top_k
            )

            if isinstance(results, dict) and 'documents' in results:
                docs = results['documents']
                if docs and len(docs) > 0 and docs[0]:
                    return docs[0]

            return []
        except Exception as e:
            print(f"Error getting the relevant documents {e}")
            return []
        

    def hybrid_search(self, query, top_k=3):
            vector_docs = self.get_relevant_documents(query, top_k=top_k)
    
            combined_docs = vector_docs.copy()
    
            try:
                bm25_docs = []
                if self.bm25 and self.all_documents:
                 tokenized_query = query.lower().split()
                 scores = self.bm25.get_scores(tokenized_query)
                 top_indices = np.argsort(scores)[::-1][:top_k]
                 bm25_docs = [self.all_documents[i] for i in top_indices if scores[i] > 0]
                 combined_docs = list(dict.fromkeys(vector_docs + bm25_docs))
            except Exception as e:
                print(f"Error in hybrid search {e}")
                return vector_docs
    
            try:
                if combined_docs:
                    pair = [[query,doc] for doc in combined_docs]
    
                    rerank_score = self.reranker.predict(pair)
    
                    scored_docs = sorted(zip(combined_docs,rerank_score),key=lambda x: x[1],reverse=True)
    
                    final_docs = [doc for doc,score in scored_docs]
    
                    return final_docs[:top_k]
            except Exception as e:
                print(f"Error in re-ranking is {e}")
                return combined_docs[:top_k]
    
    