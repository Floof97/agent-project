# backend/app/main.py
import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException, Request, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
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

app.mount("/view", StaticFiles(directory="data"), name="view")

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
    thread_id: str = "default-session"

@app.post("/chat")
async def chat_endpoint(request: ChatRequest, user_id: str = Depends(get_user_id)):
    try:
        # Using thread_id from frontend to ensure each refresh is a new session
        # 1. Use the 'thread_id' from the frontend for Memory
        config = {"configurable": {"thread_id": request.thread_id}} 
        
        # 2. Use the 'user_id' for the Vector Search (Data Isolation)
        input_data = {
            "messages": [("user", request.message)], 
            "user_id": user_id 
        }
        
        result = app_graph.invoke(input_data, config)
        return {"response": result["messages"][-1].content}
    except Exception as e:
        print(f"Error: {e}")
        return {"response": "I'm having trouble with my memory right now."}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), user_id: str = Depends(get_user_id)):
    # Unique name for the disk
    temp_filename = f"{user_id}_{file.filename}"
    file_path = os.path.join(DATA_DIR, temp_filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        process_pdf(file_path, user_id, file.filename) 
        
        return {"filename": file.filename, "status": "success"}
    except Exception as e:
        # Only delete if the upload itself failed
        if os.path.exists(file_path): os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))
    
@app.delete("/files/{filename}")
async def delete_file(filename: str, user_id: str = Depends(get_user_id)):
    print(f"🗑️ Attempting to delete: {filename} for user: {user_id}")
    
    # 1. Physical File Path (Matches what we used in /upload)
    disk_path = os.path.join(DATA_DIR, f"{user_id}_{filename}")
    
    try:
        # 2. Remove from Disk
        if os.path.exists(disk_path):
            os.remove(disk_path)
            print(f"✅ Deleted from disk: {disk_path}")
        else:
            print(f"⚠️ File not found on disk at: {disk_path}")

        # 3. Remove from Supabase (Vector DB)
        # Import the function from ingestion.py
        from app.ingestion import delete_pdf_from_supabase
        success = delete_pdf_from_supabase(filename, user_id)
        
        if success:
            return {"status": "success", "message": f"Deleted {filename}"}
        else:
            raise HTTPException(status_code=500, detail="Failed to clear database chunks")
            
    except Exception as e:
        print(f"❌ Delete Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

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