# backend/app/main.py
import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException, Request, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client, Client
from dotenv import load_dotenv

# Internal imports
from app.ingestion import process_pdf, delete_pdf_from_supabase # Updated name
from app.graph import app_graph 

load_dotenv()

app = FastAPI()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(url, key)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True, # Required for cookies/sessions
    allow_methods=["*"],
    allow_headers=["*"], # Allows 'Authorization' header
)

DATA_DIR = "data"
if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)

# --- SECURITY DEPENDENCY ---
async def get_user_id(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization Header")
    try:
        token = authorization.replace("Bearer ", "")
        user = supabase.auth.get_user(token)
        return user.user.id
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid Session")

# --- UPDATED ENDPOINTS ---

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat_endpoint(request: ChatRequest, user_id: str = Depends(get_user_id)):
    try:
        # We pass the user_id into the graph so it can filter the vector search
        config = {"configurable": {"thread_id": user_id}}
        input_data = {"messages": [("user", request.message)], "user_id": user_id}
        result = app_graph.invoke(input_data, config)
        return {"response": result["messages"][-1].content}
    except Exception as e:
        return {"response": f"Error: {str(e)}"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), user_id: str = Depends(get_user_id)):
    file_path = os.path.join(DATA_DIR, f"{user_id}_{file.filename}")
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Pass the REAL user_id to ingestion
        process_pdf(file_path, user_id)
        
        return {"filename": file.filename, "status": "success"}
    finally:
        if os.path.exists(file_path):
            os.remove(file_path) # Clean up temp file after embedding

@app.get("/files")
async def list_files(user_id: str = Depends(get_user_id)):
    # PRODUCTION MOVE: Instead of looking at a local folder, 
    # we ask Supabase for unique filenames tagged with this user_id
    response = supabase.table("document_chunks") \
        .select("metadata->source") \
        .eq("user_id", user_id) \
        .execute()
    
    # Get unique filenames from the metadata
    filenames = list(set([doc['source'] for doc in response.data if 'source' in doc]))
    return {"files": filenames}