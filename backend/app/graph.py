from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langgraph.checkpoint.memory import MemorySaver

# 1. Global Setup (Models stay the same)
embeddings = OllamaEmbeddings(model="nomic-embed-text")
llm = ChatOllama(model="llama3.2:1b", temperature=0)

# 2. Define the State
class State(TypedDict):
    messages: Annotated[list, add_messages]

# 3. Define the Logic Node
def call_model(state: State):
    user_query = state["messages"][-1].content

    # --- FRESH CONNECTION ---
    # We define the DB inside the function so it 're-scans' the folder every time
    db = Chroma(
        persist_directory="./chroma_db", 
        embedding_function=embeddings, 
        collection_name="business_FAQ_docs"
    )
    
    # --- RETRIEVAL ---
    print(f"--- 🔍 Searching Knowledge Base for: {user_query} ---")
    # We create the retriever locally so it's always up to date
    retriever = db.as_retriever(search_kwargs={"k": 3})
    docs = retriever.invoke(user_query)
    
    # --- DATA CHECK ---
    if not docs:
        return {"messages": [("assistant", "I've checked the documents, but I don't see any information on that. Can you provide more detail?")]}

    # --- RESPONSE GENERATION ---
    context = "\n\n".join([doc.page_content for doc in docs])
    
    system_instructions = f"""
     You are a professional FAQ Assistant.
    Use the following pieces of retrieved context to answer the user's question.
    Keep the answers relatively short and to the point.
    If the answer is not in the context, strictly state that you do not have that information.
    Maintain a professional and helpful tone.

    CONTEXT:
    {context}
    """
    
    # We put the system prompt at the start of the message chain
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