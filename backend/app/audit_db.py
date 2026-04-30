from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings

# 1. Setup the same connection
embeddings = OllamaEmbeddings(model="nomic-embed-text")
vector_db = Chroma(
    persist_directory="./chroma_db", 
    embedding_function=embeddings, 
    collection_name="business_FAQ_docs"
)

def check_inventory():
    # Get all metadata from the DB
    data = vector_db.get()
    metadatas = data['metadatas']
    
    if not metadatas:
        print("\n📭 The database is completely empty!")
        return

    # Count how many chunks exist for each file
    inventory = {}
    for meta in metadatas:
        source = meta.get('source', 'Unknown')
        inventory[source] = inventory.get(source, 0) + 1

    print("\n--- 📊 Current Database Inventory ---")
    for source, count in inventory.items():
        print(f"📄 File: {source} | 🧩 Chunks: {count}")
    print("------------------------------------\n")

if __name__ == "__main__":
    check_inventory()