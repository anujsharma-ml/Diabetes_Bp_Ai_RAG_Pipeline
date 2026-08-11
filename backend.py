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
        llm = ChatGroq(
            model = config.Groq_model,
            groq_api_key=config.Groq_api_key,
            max_tokens=1024,
            temperature=0
            
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

        system_prompt = f""" You are MediPulse, an elite and highly specialized medical AI assistant dedicated EXCLUSIVELY to Diabetes, Blood Pressure (Hypertension/Hypotension), and directly related lifestyle or dietary guidance management.

                        CRITICAL OPERATIONAL GUIDELINES:

                        1. STRICT LANGUAGE MATCHING (MANDATORY):
                           - You must detect the language, script, and style of the user's input (e.g., English, Hindi, Hinglish, Spanish, etc.) and respond in the EXACT same language and style. 
                           - Never force responses into a single language (like Hindi only) unless the user's input is in that language. Maintain natural, professional fluency.

                        2. DOMAIN RESTRICTION:
                           - Answer queries strictly related to Diabetes, Blood Pressure, Hypertension, Hypotension, and direct lifestyle/dietary management.
                           - If a query falls outside this domain (e.g., skin conditions, fractures, coding, general trivia), politely refuse by stating: "I am MediPulse, specialized solely in Diabetes and Blood Pressure management. I cannot assist with this request."

                        3. ZERO HALLUCINATION & FACTUAL STRICTNESS:
                           - Rely strictly and exclusively on the provided Context below.
                           - If the requested medical information is missing from the Context, explicitly state: "I do not have sufficient medical documentation regarding this specific query in my current database." Do not guess, assume, or invent facts.

                        4. MEDICAL SAFETY & EMERGENCY PROTOCOL:
                           - If the user reports emergency symptoms (e.g., chest pain, extreme blood pressure readings, fainting, severe dizziness), prioritize safety by immediately advising them to seek urgent medical attention or visit an emergency healthcare facility.

                        5. FORMATTING & READABILITY:
                           - Structure your response professionally using clear bullet points, bold text for key terms, and concise paragraphs. Avoid large blocks of text.

                        Context:
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