from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_groq import ChatGroq
import config
import os
from rag_core import file_loader, chunks_splitter, RagPipeline

os.environ["GROQ_API_KEY"] = config.Groq_api_key

app = FastAPI(title="Dibetes and bp helpfull ai assistance")


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
            max_tokens=1024,
            temperature=0.2,
            
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

        relevant_docs = rag_pipeline.get_relevant_documents(user_query)

        context_text = "\n\n".join(relevant_docs)


        system_prompt = f"""You are a strict and professional medical assistant chatbot specialized ONLY in Diabetes and Hypertension (BP). 
                        Your job is to answer the user's question using ONLY the provided context text below.

                        Strict Rules:
                        1. If the user asks anything outside of Diabetes, Hypertension, or their related symptoms/treatments, you must reply: "I can only answer questions related to diabetes and blood pressure."
                        2. If the answer cannot be found in the context text, you must reply: "I have no information about this in my medical records."
                        3. Do not make up facts or use external knowledge outside of the given context.

                       Context Text:
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



    





@app.get("/")
def home():
    return {"message": "Hello, FastAPI sikh rahe hain!"}