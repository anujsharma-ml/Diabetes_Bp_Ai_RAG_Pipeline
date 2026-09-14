import config
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_groq import ChatGroq
from fastapi.concurrency import run_in_threadpool
from rag_core import RagPipeline
from prompt import SYSTEM_PROMPT_TEMPLATE

app = FastAPI(title="MediPulse AI Assistance", debug=True)

# ------ Initialize RAG Pipeline (Without Blocking Ingestion Loop) ------
print("Connecting to Rag Pipeline...")
rag_pipeline = RagPipeline()

# ------ LLM Architecture ------
try:
    llm = ChatGroq(
        model=config.Groq_model,
        api_key=config.Groq_api_key,
        max_tokens=1024,
        temperature=0.2
    )
except Exception as e:
    print(f"Error in LLM Architecture: {e}")


# ------ Pydantic Models ------
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    query: str
    history: List[Message] = []


# ------ Chat Endpoint ------
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        user_query = request.query
        chat_history = request.history

        relevant_docs = await run_in_threadpool( rag_pipeline.hybrid_search,user_query,top_k=3)
        context_text = "\n\n".join(relevant_docs)

        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(context_text=context_text)
        
        message_to_send = [SystemMessage(content=system_prompt)]

        for msg in chat_history:
            if msg.role == "user":
                message_to_send.append(HumanMessage(content=msg.content))
            else:
                message_to_send.append(AIMessage(content=msg.content))
                
        message_to_send.append(HumanMessage(content=user_query))

        async def generate():
            async for chunk in llm.astream(message_to_send):
                if chunk.content:
                    yield chunk.content

        return StreamingResponse(generate(), media_type="text/plain")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def read_root():
    return {"status": "Active", "message": "Backend is running successfully!"}