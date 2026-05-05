import os
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langgraph.checkpoint.memory import MemorySaver
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# 1. Global Setup (Models stay the same)
embeddings = OllamaEmbeddings(model="nomic-embed-text")
llm = ChatOllama(model="llama3.2:1b", temperature=0)
# llm = ChatOllama(model="gemma4:e2b", temperature=0)
# llm = ChatOllama(model="gemma4:eb", temperature=0)

# Initialize Supabase
supabase: Client = create_client(
    os.environ.get("SUPABASE_URL"), 
    os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
)

# 2. Define the State
class State(TypedDict):
    messages: Annotated[list, add_messages]
    user_id: str # We keep this so we can filter by user

# 3. Define the Logic Node (Back to your original structure)
def call_model(state: State):
    user_query = state["messages"][-1].content
    user_id = state.get("user_id", "default-user")

    # --- RETRIEVAL (The Supabase Way) ---
    print(f"--- 🔍 Searching Knowledge Base for: {user_query} ---")
    
    # 1. Embed the user query
    query_vector = embeddings.embed_query(user_query)

    # 2. Search Supabase using the match_documents function
    response = supabase.rpc('match_documents', {
        'query_embedding': query_vector,
        'match_threshold': 0.5, 
        'match_count': 3
    }).execute()
    
    docs = response.data

    # --- DATA CHECK ---
    if docs:
        context = "\n\n".join([doc['content'] for doc in docs])
        print(f"✅ Found {len(docs)} relevant chunks in Supabase.")
    else:
        context = "No specific documents have been uploaded or found for this query."
        print("ℹ️ No documents found. Falling back to general knowledge.")

    system_instructions = f"""
    You are a professional FAQ Assistant.
    If the user is greeting or having a casual conversation, just do the same.
    Use the following pieces of retrieved context to answer the user's question.
    Keep the answers relatively short and to the point.
    If the answer is not in the context, strictly state that you do not have that information.
    Maintain a professional and helpful tone.

    CONTEXT:
    {context}
    """
    
    messages_for_llm = [("system", system_instructions)] + state["messages"]
    
    response = llm.invoke(messages_for_llm)
    return {"messages": [response]}

# 4. Build the Graph
workflow = StateGraph(State)
workflow.add_node("agent", call_model)
workflow.add_edge(START, "agent")
workflow.add_edge("agent", END)

# 5. Memory & Compilation
memory = MemorySaver()
app_graph = workflow.compile(checkpointer=memory)