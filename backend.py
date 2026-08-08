from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_groq import ChatGroq
import config
import os
from rag_core import file_loader, chunks_splitter, RagPipeline

app = FastAPI(title="Dibetes and bp helpfull ai assistance",debug=True)


#------  rag_pipeline -----------

print("Intializing the Rag Pipeline...")

rag_pipeline = RagPipeline()  
try:

    if rag_pipeline.collection.count()==0:
        print("The Database is empty  loading files on it..")

        documents = file_loader(config.file_path)
        all_chunks = chunks_splitter(documents)
        rag_pipeline.add_documents(all_chunks)

    else:
        print("The database is already filled...")
except Exception as e:
    print(f"The exception is in loading the rag_pipeline {e}")



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



#---- Chat Endpoint------

@app.post("/chat")
def chat_endpoint(request:ChatRequest):
    try:
        user_query = request.query
        chat_history = request.history

        relevant_docs = rag_pipeline.hybrid_search(user_query)

        

        context_text = "\n\n".join(relevant_docs)


        system_prompt = f""" You are MediPulse, an elite medical AI assistant specialized EXCLUSIVELY in Diabetes and Blood Pressure (Hypertension/Hypotension) management.

                           CRITICAL BOUNDARIES & SCOPE:
                           1. DOMAIN RESTRICTION: You answer queries ONLY related to Diabetes, Blood Pressure, Hypertension, Hypotension, and directly linked lifestyle/dietary guidance.
                              - If the query is unrelated to Diabetes or Blood Pressure (e.g., cancer, skin issues, fractures, coding, trivia), politely refuse: State clearly that you are solely specialized in Diabetes and Blood Pressure management.

                           2. ZERO HALLUCINATION & FACTUAL STRICTNESS:
                              - Rely strictly on the provided Context below.
                              - If the requested information about Diabetes or BP is NOT present in the provided Context, explicitly and politely state: "I do not have sufficient medical documentation regarding this specific query in my current database." Do NOT invent or guess any facts.

                           3. DYNAMIC MULTILINGUAL & LANGUAGE MATCHING:
                              - Always respond in the EXACT same language and style used by the user (e.g., Hinglish, English, Hindi, Spanish, French, etc.).
                              - Output must be grammatically correct, natural, professional, and clear. Avoid word-by-word broken translations.

                           4. MEDICAL SAFETY & EMERGENCY DISCLAIMER:
                              - If the user describes severe or emergency symptoms (e.g., extremely high/low BP readings, chest pain, dizziness, fainting), immediately advise them to consult a qualified doctor or visit an emergency healthcare facility.

                           5. FORMATTING & READABILITY:
                              - Keep answers structured, easy to read, and concise. Use bullet points and bold text where appropriate instead of huge blocks of text.
                           
                           Context:
                           {context_text}"""
        
        message_to_send = [SystemMessage(content=system_prompt)]

        for msg in chat_history:
            if msg.role=="user":
                message_to_send.append(HumanMessage(content=msg.content))
            else:
                message_to_send.append(AIMessage(content=msg.content))
                
        message_to_send.append(HumanMessage(content=user_query))

        response = llm.invoke(message_to_send)

        return {"answer": response.content}
    

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



