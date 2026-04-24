from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver

# 1. Define the State (What the agent remembers)
class State(TypedDict):
    # add_messages ensures new messages are appended to history, not overwriting it
    messages: Annotated[list, add_messages]

# 2. Initialize the Local LLM
llm = ChatOllama(model="llama3.2:1b", temperature=0.7)

# 3. Define the Logic Node
def call_model(state: State):
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

# 4. Build the Graph
workflow = StateGraph(State)
workflow.add_node("agent", call_model)
workflow.add_edge(START, "agent")
workflow.add_edge("agent", END)

# 5. Add Memory (The Checkpointer)
memory = MemorySaver()
app_graph = workflow.compile(checkpointer=memory)