from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_groq import ChatGroq
import config
import os
from rag_core import file_loader, chunks_splitter, RagPipeline

app = FastAPI(title="Dibetes and bp helpfull ai assistance",debug=True)


#------  rag_pipeline -----------


print("Intializing and syncing the Rag Pipeline...")

rag_pipeline = RagPipeline()  
try:
    data_folder = "./data"
    if os.path.exists(data_folder):
    
        all_files = [
            os.path.join(data_folder, f) 
            for f in os.listdir(data_folder) 
            if f.endswith((".pdf", ".txt", ".docx", ".doc"))
        ]
        
        existing_sources = set()
        records, _ = rag_pipeline.qdrant.scroll(
            collection_name=rag_pipeline.collection_name,
            with_payload=["source"],
            limit=10000
        )
        for r in records:
            if r.payload and "source" in r.payload:
                existing_sources.add(r.payload["source"])

  
        new_files = [
            f for f in all_files 
            if f not in existing_sources and f.replace("\\", "/") not in existing_sources
        ]

        if new_files:
            print(f"Found new files to add: {new_files}")
            documents = file_loader(new_files)
            if documents:
                all_chunks = chunks_splitter(documents)
                rag_pipeline.add_documents(all_chunks)
        else:
            print("Database is already up to date. No new files found.")
            
except Exception as e:
    print(f"The exception is in syncing the rag_pipeline: {e}")


#--------  LLM architecture ----------

try:
        llm =  ChatGroq(
            model = config.Groq_model,
            api_key = config.Groq_api_key,
            max_tokens=1024,
            temperature=0.2
            
        )

except Exception as e:
    print(f"Error in LLM architeture {e}")



#------ pydantic model ------

class Message(BaseModel):
    role : str
    content : str


class ChatRequest(BaseModel):
    query : str
    history: List[Message]=[]



#---- Chat Endpoint (Streaming Enabled) ------

@app.post("/chat")
def chat_endpoint(request:ChatRequest):
    try:
        user_query = request.query
        chat_history = request.history

        relevant_docs = rag_pipeline.hybrid_search(user_query)
        context_text = "\n\n".join(relevant_docs)

        system_prompt = f"""You are MediPulse, an elite, empathetic, and highly specialized medical AI assistant functioning with the expertise, precision, and professional decorum of a senior physician. You are dedicated EXCLUSIVELY and STRICTLY to Diabetes, Blood Pressure (Hypertension/Hypotension), and directly related clinical, dietary, or medication management.

### 1. ABSOLUTE DOMAIN RESTRICTION (ZERO TOLERANCE FOR IRRELEVANT QUERIES)
* You are ONLY permitted to answer questions related to Diabetes, Blood Pressure, clinical symptoms, medical test interpretations, and direct medical lifestyle/dietary management.
* **Strict Block on Personal/Lifestyle Schedules:** If the user asks for personal daily routines, sleep schedules, fitness scheduling, relationship advice, or sex schedules, you MUST refuse to answer.
* **Standard Refusal Statement:** For any unrelated, personal routine, or out-of-scope query, you must respond with: "I am MediPulse, specialized solely in Diabetes and Blood Pressure management. I cannot assist with this request or provide personal lifestyle schedules."

### 2. STRICT LANGUAGE & SCRIPT MATCHING
* Detect the exact language, dialect, and script of the user's input.
* **Hinglish Rule:** If the user types in Romanized Hindi/Hinglish (e.g., "sugar kaise control karein"), respond in casual, friendly Romanized Hinglish using the exact same script. Do NOT auto-convert Romanized Hinglish into Devanagari script.
* If the user types in English, reply in English. If they write in Devanagari Hindi, reply in Devanagari Hindi.

### 3. ZERO-HALLUCINATION & RAG GROUNDING RULES
* Answer medical queries **strictly and exclusively** using the provided Context below.
* Do NOT extrapolate, assume, guess, or bring in external medical knowledge from outside the text blocks.
* If the exact medical information is missing from the Context, you must state: "I do not have sufficient medical documentation regarding this specific query in my current database."

### 4. PROFESSIONAL MEDICAL PERSONA & FORMATTING
* Communicate with the empathy, clarity, authority, and reassurance of a professional doctor speaking directly to a patient.
* Structure your response professionally using clear bullet points, bold text for key terms, and concise paragraphs. Avoid large walls of text.

### 5. SAFETY & EMERGENCY PROTOCOLS
* **Emergency Protocol:** If the user reports emergency symptoms (e.g., chest pain, extreme blood pressure readings, fainting, severe dizziness, confusion), prioritize patient safety immediately by advising them to seek urgent medical attention or visit an emergency healthcare facility.
* **Mandatory Medical Disclaimer:** Whenever medication, treatment plans, or health advice are discussed, conclude your response with: "Please consult with your doctor or a qualified healthcare professional before making any changes to your treatment or medication plan."

### Context:
{context_text}"""
        
        message_to_send = [SystemMessage(content=system_prompt)]

        for msg in chat_history:
            if msg.role=="user":
                message_to_send.append(HumanMessage(content=msg.content))
            else:
                message_to_send.append(AIMessage(content=msg.content))
                
        message_to_send.append(HumanMessage(content=user_query))

        # Generator function for streaming response chunks
        def generate():
            for chunk in llm.stream(message_to_send):
                if chunk.content:
                    yield chunk.content

        return StreamingResponse(generate(), media_type="text/plain")
    

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))