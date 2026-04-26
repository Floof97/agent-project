import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

# 1. Setup the Embedding Model (The "Translator")
embeddings = OllamaEmbeddings(model="nomic-embed-text")

def process_pdf(file_path: str, collection_name: str):
    print(f"--- Starting Ingestion for: {file_path} ---")
    
    # 2. Load the PDF (Page by Page to save RAM)
    loader = PyPDFLoader(file_path)
    # lazy_load() is better for huge files
    pages = []
    for page in loader.lazy_load():
        pages.append(page)
    
    print(f"Total pages loaded: {len(pages)}")

    # 3. Chunking (The Secret to Precision)
    # For business docs, we use a smaller chunk size with overlap
    # This ensures context isn't cut off mid-sentence
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800, 
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
    
    print("--- Ingestion Complete! ---")
    return vector_db


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
    else:
        print(f"Error: Could not find the file at {TEST_PDF_PATH}")
        print("Please put a PDF in the folder and update the TEST_PDF_PATH variable.")