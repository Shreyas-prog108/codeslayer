# graph.py
from langgraph.graph import StateGraph, MessagesState
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver

def create_sales_agent_graph():
    # Initialize a local Ollama model (offline)
    model = ChatOllama(model="llama3")  # or "mistral" if lighter

    # Create the state graph (required schema: MessagesState)
    graph = StateGraph(MessagesState)

    # Define the logic for your agent
    def sales_agent_node(state):
        user_message = state["messages"][-1].content
        response = model.invoke(user_message)
        return {"messages": [{"role": "assistant", "content": response.content}]}

    # Add node to the graph
    graph.add_node("sales_agent", sales_agent_node)

    # Define entry and finish points
    graph.set_entry_point("sales_agent")
    graph.set_finish_point("sales_agent")

    # Memory to hold conversations
    memory = MemorySaver()

    # Compile the graph
    app = graph.compile(checkpointer=memory)
    return app
