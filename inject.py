# ingest.py
import os
from rag_core import file_loader, chunks_splitter, RagPipeline

def run_ingestion():
    print("🚀 Starting Data Ingestion Script...")
    rag_pipeline = RagPipeline()
    data_folder = "./data"
    
    if not os.path.exists(data_folder):
        print("❌ Data folder not found!")
        return

    all_files = [
        os.path.join(data_folder, f) 
        for f in os.listdir(data_folder) 
        if f.endswith((".pdf", ".txt", ".docx", ".doc"))
    ]

    existing_sources = set()
    try:
        records, _ = rag_pipeline.qdrant.scroll(
            collection_name=rag_pipeline.collection_name,
            with_payload=["source"],
            limit=10000
        )
        for r in records:
            if r.payload and "source" in r.payload:
                existing_sources.add(r.payload["source"])
    except Exception as e:
        print(f"⚠️ Warning while checking existing vectors: {e}")

    new_files = [
        f for f in all_files 
        if f not in existing_sources and f.replace("\\", "/") not in existing_sources
    ]

    if new_files:
        print(f"📄 Found {len(new_files)} new files to ingest: {new_files}")
        documents = file_loader(new_files)
        if documents:
            chunks = chunks_splitter(documents)
            rag_pipeline.add_documents(chunks)
            print("✅ Ingestion Completed Successfully!")
    else:
        print("🎉 Vector database is already up to date. No new files found.")

if __name__ == "__main__":
    run_ingestion()