"""Graph orchestration for Scout Agent."""
from langgraph.graph import StateGraph, END

from src.models import AgentState
from src.agents.nodes import (
    strategist_node,
    retriever_node,
    architect_node,
    mentor_node,
)


def create_scout_graph():
    """
    Create and compile the Scout Agent workflow graph.
    
    Graph structure:
    1. Strategist: Expand user query into search strategies
    2. Retriever: Search GitHub and rank results
    3. Architect: Extract and analyze code
    4. Mentor: Compare findings
    
    Returns:
        Compiled StateGraph workflow
    """
    workflow = StateGraph(AgentState)

    # Add Nodes
    workflow.add_node("strategist", strategist_node)
    workflow.add_node("retriever", retriever_node)
    workflow.add_node("architect", architect_node)
    workflow.add_node("mentor", mentor_node)

    # Define Edges
    workflow.set_entry_point("strategist")
    workflow.add_edge("strategist", "retriever")

    # Conditional Logic: Should we continue?
    def should_analyze(state: AgentState):
        if not state["raw_repos"]:
            return "end"
        return "continue"

    workflow.add_conditional_edges(
        "retriever",
        should_analyze,
        {
            "continue": "architect",
            "end": END
        }
    )

    workflow.add_edge("architect", "mentor")
    workflow.add_edge("mentor", END)

    return workflow.compile()
