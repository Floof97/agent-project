from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_ollama import ChatOllama

app = FastAPI()

# Enable CORS so your Next.js site can talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Gemma 4 (use e2b since it fits your RAM)
llm = ChatOllama(model="gemma4:e2b", temperature=0.7)

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        print(f"Received message: {request.message}") # Debugging
        
        # Ensure we are getting a clean string back
        response = llm.invoke(request.message)
        
        # Some versions of LangChain return an object, we need the .content
        ai_text = response.content if hasattr(response, 'content') else str(response)
        
        print(f"AI Response: {ai_text}") # Debugging
        return {"response": ai_text}
        
    except Exception as e:
        print(f"Error in backend: {e}")
        return {"response": "I encountered an error while thinking."}