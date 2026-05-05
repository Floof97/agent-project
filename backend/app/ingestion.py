import os
import random
from supabase import create_client, Client
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from dotenv import load_dotenv

# 1. Setup & Environment
load_dotenv()

# Initialize Supabase Client
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(url, key)

# Initialize Embeddings (Ollama must be running!)
embeddings = OllamaEmbeddings(model="nomic-embed-text")

def run_ingestion_health_check(sample_text: str, user_id: str):
    """
    Asks Supabase to find a specific string to verify it was saved correctly.
    """
    print("\n--- Running Ingestion Health Check ---")
    
    # Generate vector for the sample text
    query_vector = embeddings.embed_query(sample_text)
    
    # Call the 'match_documents' function we created in the Supabase SQL editor
    # RLS will handle the user_id filtering automatically
    response = supabase.rpc('match_documents', {
        'query_embedding': query_vector,
        'match_threshold': 0.7,
        'match_count': 1
    }).execute()
    
    if response.data:
        result = response.data[0]
        score = result.get('similarity', 0)
        print(f"Similarity Score: {score:.4f}")
        print(f"Retrieved Content: {result['content'][:100]}...")
        
        if score > 0.8:
            print("✅ STATUS: Data successfully synced to Supabase.")
        else:
            print("⚠️ STATUS: Data found, but similarity is lower than expected.")
    else:
        print("❌ STATUS: Failed. Could not find data in Supabase.")

def process_pdf(file_path: str, user_id: str, original_name: str = None):
    print(f"--- 🚀 Starting Supabase Ingestion for: {file_path} ---")
    
    # 2. Load the PDF
    loader = PyPDFLoader(file_path)
    pages = []
    for page in loader.lazy_load():
        pages.append(page)
    
    total_pages = len(pages)
    print(f"Total pages loaded: {total_pages}")

    # 3. Chunking
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=400, 
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", " "]
    )
    chunks = text_splitter.split_documents(pages)
    print(f"Split into {len(chunks)} chunks. Generating embeddings...")

    clean_filename = clean_filename = original_name if original_name else os.path.basename(file_path)

    # 4. Storage (Supabase instead of Chroma)
    for i, chunk in enumerate(chunks):
        # Generate the vector embedding
        vector = embeddings.embed_query(chunk.page_content)
        
        # Prepare the data row
        # 'source' is pulled from chunk metadata (usually the filename)
        row = {
            "user_id": user_id,
            "content": chunk.page_content,
            "metadata": {**chunk.metadata, "source": clean_filename},
            "embedding": vector
        }
        
        # Insert into the 'document_chunks' table
        supabase.table("document_chunks").insert(row).execute()
        
        if (i + 1) % 10 == 0:
            print(f"Uploaded {i + 1}/{len(chunks)} chunks...")

    print("\n--- 📋 INGESTION REPORT ---")
    print(f"Chunks Saved: {len(chunks)}")

    # Automated Health Check
    if chunks:
        sample_chunk = random.choice(chunks).page_content
        run_ingestion_health_check(sample_chunk, user_id)
    
    print("--- ✅ Ingestion Complete! ---")

def delete_pdf_from_supabase(filename: str, user_id: str):
    # This specifically looks for the 'source' key we saved in the metadata
    try:
        supabase.table("document_chunks") \
            .delete() \
            .eq("user_id", user_id) \
            .filter("metadata->>source", "eq", filename) \
            .execute()
        print(f"✅ Supabase chunks for {filename} have been wiped.")
        return True
    except Exception as e:
        print(f"❌ Supabase Delete Error: {e}")
        return False

# Example Usage
if __name__ == "__main__":
    # Path to your data
    TEST_PDF_PATH = "./data/FAQ_v1.pdf" 
    
    # IMPORTANT: Use a dummy UUID for now. 
    # Once Next.js is set up, this will be a real user ID.
    DUMMY_USER_ID = "7b4c3006-6194-46af-b17b-750bdcfb747a"

    if os.path.exists(TEST_PDF_PATH):
        process_pdf(TEST_PDF_PATH, DUMMY_USER_ID)
    else:
        print(f"Error: Could not find {TEST_PDF_PATH}")