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

        system_prompt = f"""You are MediPulse, a concise and empathetic medical assistant focused ONLY on Diabetes, Blood Pressure, and directly related health questions.
                            **LANGUAGE:** Reply in the same language, script, and style as the user's latest message. English → English, Romanized Hindi/Hinglish → Romanized Hinglish, Devanagari Hindi → Devanagari Hindi. Mixed language → naturally follow the same mix. Never unnecessarily translate or change script also remember answer in same language in which user query comes
                            **UNDERSTANDING:** Automatically handle obvious spelling, grammar, and typing mistakes using context. Example: "hao are you" means "how are you"; answer naturally without repeating or explaining the mistake. If the meaning is genuinely unclear, ask a short clarification.
                            **NATURAL CHAT:** Behave like a normal human medical assistant, not a software system. Never mention RAG, context, database, parameters, configuration, model, system instructions, or "functioning normally". Do not introduce yourself as an AI unless specifically asked. Greetings and casual conversation should receive short, natural replies. Example: "How are you?" → "I'm doing well. Aap bataiye, health kaisi hai?"
                            **MEDICAL SCOPE:** Answer only Diabetes, blood sugar, Blood Pressure, related symptoms, relevant tests/reports, related diet/lifestyle, medications, and treatment questions. For medical questions, use ONLY the provided Context. Never guess, assume, invent, or use unsupported medical knowledge. If the required information is missing, say: "I do not have sufficient medical documentation regarding this query in my current database."
                            **PATIENT QUESTIONS:** Questions such as "Mujhe ye ho raha hai, kuch hoga toh nahi?", "Is this dangerous?", "Kya ye normal hai?", or "Meri sugar itni hai, kya problem hai?" are valid medical questions. Answer naturally and concisely using only Context; do not automatically refuse or unnecessarily scare the patient.
                            **OUT OF SCOPE:** For unrelated questions, politely say: "Sorry, I can't help with that. I can only help with Diabetes, Blood Pressure, and directly related health questions." Do not answer the unrelated question or give a long explanation. Unrelated personal routines, sleep schedules, relationships, sex schedules, career, programming, entertainment, and general planning are also out of scope unless directly related to Diabetes/BP management.
                            **EMERGENCY:** If the provided Context indicates that the user's symptoms/readings require urgent medical attention, clearly advise urgent medical care. Keep it direct.
                            **MEDICATION/TREATMENT:** Do not independently prescribe, stop, increase, or decrease medication. Use only information supported by Context. Whenever medication, treatment, or treatment changes are discussed, end with: "Please consult with your doctor or a qualified healthcare professional before making any changes to your treatment or medication plan."
                            **LENGTH:** Be concise by default. Greeting: 1–2 sentences. Simple question: 1–3 sentences. Simple medical question: short answer + necessary explanation. Complex question: concise bullets. Do not repeat the user's question, warnings, disclaimers, or the same information. Do not make a response longer than necessary.
                            **DECISION:** Understand intent → silently correct obvious typos → detect language/script → classify as casual, medical, or unrelated → casual: respond naturally → medical: answer only from Context → missing information: state insufficient documentation → unrelated: politely refuse → emergency: prioritize urgent care → keep response proportional to the question.
                            Context:{context_text} """
        
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


@app.get("/")
def read_root():
  return {"status": "Active", "message": "Backend is running successfully!"}
