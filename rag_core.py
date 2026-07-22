import os
import chromadb
import uuid
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import config

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
    def __init__(self, drive_path=config.databas_path):
        self.client = chromadb.PersistentClient(path=drive_path)
        self.collection = self.client.get_or_create_collection(name="collection")
        self.embedding_model = SentenceTransformer(config.Embedding_model)

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