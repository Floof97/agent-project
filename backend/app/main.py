from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.graph import app_graph  # Import your new graph

app = FastAPI()

# Enable CORS so your Next.js site can talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    thread_id: str = "default-user" # Added for memory tracking

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        # Configuration for memory (points to a specific conversation)
        config = {"configurable": {"thread_id": request.thread_id}}
        
        # Run the graph
        # We pass the input as a "user" message
        input_data = {"messages": [("user", request.message)]}
        result = app_graph.invoke(input_data, config)
        
        # Get the last message (the AI's response) from the state
        ai_response = result["messages"][-1].content
        
        return {"response": ai_response}
    except Exception as e:
        print(f"Graph Error: {e}")
        return {"response": "My memory circuits are fuzzy. Error occurred."}