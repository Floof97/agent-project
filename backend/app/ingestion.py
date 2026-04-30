import os
import random
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

# 1. Setup the Embedding Model (The "Translator")
embeddings = OllamaEmbeddings(model="nomic-embed-text")

def run_ingestion_health_check(vector_db, sample_text: str):
    """
    Tests if the DB can find a specific known string from the PDF.
    High similarity score = Successful ingestion.
    """
    print("\n--- Running Ingestion Health Check ---")
    
    # Search the DB for the sample text
    results = vector_db.similarity_search_with_relevance_scores(sample_text, k=1)
    
    if results:
        doc, score = results[0]
        print(f"Similarity Score: {score:.4f} (Target: > 0.7)")
        print(f"Retrieved Content: {doc.page_content[:100]}...")
        
        if score > 0.8:
            print("✅ STATUS: High Accuracy. Data is well-represented.")
        elif score > 0.6:
            print("⚠️ STATUS: Moderate Accuracy. Consider adjusting chunk size.")
        else:
            print("❌ STATUS: Low Accuracy. Retrieval is struggling.")
    else:
        print("❌ STATUS: Failed. No data found for the sample text.")

def process_pdf(file_path: str, collection_name: str):
    print(f"--- Starting Ingestion for: {file_path} ---")
    
    # 2. Load the PDF (Page by Page to save RAM)
    loader = PyPDFLoader(file_path)
    # lazy_load() is better for huge files
    pages = []
    for page in loader.lazy_load():
        pages.append(page)
    
    total_pages = len(pages)
    print(f"Total pages loaded: {total_pages}")

    # 3. Chunking (The Secret to Precision)
    # For business docs, we use a smaller chunk size with overlap
    # This ensures context isn't cut off mid-sentence
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=400, 
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", " "]
    )
    chunks = text_splitter.split_documents(pages)
    print(f"Split into {len(chunks)} chunks.")

    # 4. Storage (Vector Database)
    # This creates a folder named 'vector_db' in your project
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory="./chroma_db",
        collection_name=collection_name
    )

    # 5. Automatic Health Check Reporting after each pdf file has been added
    print("\n--- 📋 INGESTION REPORT ---")
    # Page Count Verification
    all_data = vector_db.get()
    indexed_pages = len(set(m.get('page') for m in all_data['metadatas'] if m.get('page') is not None))
    print(f"Indexed Pages: {indexed_pages} / {total_pages}")

    # Automated Health Check (Grabs a random chunk to see if it can find itself)
    if chunks:
        sample_chunk = random.choice(chunks).page_content
        run_ingestion_health_check(vector_db, sample_chunk)
    print("--- Ingestion Complete! ---")

    return vector_db

def delete_pdf_from_db(filename: str, collection_name: str):
    """
    Removes all chunks associated with a specific filename from ChromaDB.
    """
    print(f"--- 🗑️ Deleting {filename} from {collection_name} ---")
    vector_db = Chroma(
        persist_directory="./chroma_db", 
        embedding_function=embeddings, 
        collection_name=collection_name
    )
    # Chroma allows deleting by metadata filter
    vector_db.delete(where={"source": filename})
    print(f"--- ✅ {filename} deleted from Vector DB ---")


# Example usage (uncomment to run manually):

# 1. Path to a test PDF (start with a small one, then try the 500-pager)
# Make sure this file actually exists in your project folder!
TEST_PDF_PATH = "FAQ_v1.pdf" 

# 2. Give your collection a name (like a table name in a database)
COLLECTION_NAME = "business_FAQ_docs"

if __name__ == "__main__":
    if os.path.exists(TEST_PDF_PATH):
        print("File found! Starting the engine...")
        process_pdf(TEST_PDF_PATH, COLLECTION_NAME)

        # WANT TO RUN A MANUAL SEARCH TEST?
        # You can uncomment the line below to test a specific question manually:
        # db = process_pdf(TEST_PDF_PATH, COLLECTION_NAME)
        # run_health_check(db, "What is the return policy?")

    else:
        print(f"Error: Could not find the file at {TEST_PDF_PATH}")
        print("Please put a PDF in the folder and update the TEST_PDF_PATH variable.")