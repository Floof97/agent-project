import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Internal imports
from app.ingestion import process_pdf, delete_pdf_from_db
from app.graph import app_graph 

app = FastAPI()

# Enable CORS so your Next.js site can talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# This lets you visit http://localhost:8000/view/yourfile.pdf in a browser
app.mount("/view", StaticFiles(directory=DATA_DIR), name="view")

# --- CHAT ENDPOINT ---
class ChatRequest(BaseModel):
    message: str
    thread_id: str = "default-user"

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        config = {"configurable": {"thread_id": request.thread_id}}
        input_data = {"messages": [("user", request.message)]}
        result = app_graph.invoke(input_data, config)
        ai_response = result["messages"][-1].content
        return {"response": ai_response}
    except Exception as e:
        print(f"Graph Error: {e}")
        return {"response": "I encountered an error processing your request."}

# --- FILE MANAGEMENT ENDPOINTS ---

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(DATA_DIR, file.filename)
    try:
        # 1. Save the file physically to the 'data' folder
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 2. Run Ingestion to add to ChromaDB
        process_pdf(file_path, "business_FAQ_docs")
        
        return {"filename": file.filename, "status": "success"}
    except Exception as e:
        print(f"Upload Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files")
async def list_files():
    if not os.path.exists(DATA_DIR):
        return {"files": []}
    # Filter out hidden files (anything starting with '.')
    files = [f for f in os.listdir(DATA_DIR) if not f.startswith('.')]
    return {"files": files}

@app.delete("/files/{filename}")
async def delete_file(filename: str):
    file_path = os.path.join(DATA_DIR, filename)
    if os.path.exists(file_path):
        # 1. Remove from local disk
        os.remove(file_path)
        # 2. Remove from Vector DB
        delete_pdf_from_db(file_path, "business_FAQ_docs")
        return {"status": "deleted"}
    
    raise HTTPException(status_code=404, detail="File not found")