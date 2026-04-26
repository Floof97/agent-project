from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langgraph.checkpoint.memory import MemorySaver

# 1. Setup the "Librarian" (The Vector Search/RAG Engine)
# This points to the folder created by your ingestion script
embeddings = OllamaEmbeddings(model="nomic-embed-text")
vector_db = Chroma(
    persist_directory="./chroma_db", 
    embedding_function=embeddings,
    collection_name="business_FAQ_docs"
)
# We ask for the top 3 most relevant chunks from the PDF
retriever = vector_db.as_retriever(search_kwargs={"k": 3})

# 2. Define the State
class State(TypedDict):
    messages: Annotated[list, add_messages]

# 3. Initialize the Local LLM
# Note: Temperature to 0. It makes the AI more "serious" and less likely to hallucinate
llm = ChatOllama(model="llama3.2:1b", temperature=0)

# 4. Define the Logic Node (RAG Logic)
def call_model(state: State):
    # Grab the very last thing the user said
    user_query = state["messages"][-1].content
    
    # Search the vector database for facts
    print(f"--- Searching Knowledge Base for: {user_query} ---")
    docs = retriever.invoke(user_query)
    
    # Combine the found chunks into one block of text
    context = "\n\n".join([doc.page_content for doc in docs])
    
    # This System Prompt "forces" the AI to stick to the facts in your PDF
    system_instructions = f"""
    You are a professional FAQ Assistant. 
    Use the following pieces of retrieved context to answer the user's question.
    If the answer is not in the context, strictly state that you do not have that information.
    Maintain a professional and helpful tone.

    CONTEXT:
    {context}
    """
    
    # We combine the system instructions with the full chat history
    full_prompt = [("system", system_instructions)] + state["messages"]
    
    response = llm.invoke(full_prompt)
    return {"messages": [response]}

# 5. Build the Graph
workflow = StateGraph(State)
workflow.add_node("agent", call_model)
workflow.add_edge(START, "agent")
workflow.add_edge("agent", END)

# 6. Memory & Compilation
memory = MemorySaver()
app_graph = workflow.compile(checkpointer=memory)