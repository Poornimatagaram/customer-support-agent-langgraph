"""
main.py

Wires all 10 nodes into the complete customer support agent graph,
matching the workflow designed in Step 1:

classify_email -> understand_problem -> search_crm -> search_knowledge_base
-> determine_resolution -> create_ticket -> draft_response -> risk_evaluation
-> [conditional: human_approval OR straight to send_response] -> send_response
"""

from langgraph.graph import StateGraph, START, END

from nodes.state import AgentState
from nodes.classify_email import classify_email
from nodes.understand_problem import understand_problem
from nodes.search_crm import search_crm
from nodes.search_knowledge_base import search_knowledge_base
from nodes.determine_resolution import determine_resolution
from nodes.create_ticket import create_ticket
from nodes.draft_response import draft_response
from nodes.risk_evaluation import risk_evaluation
from nodes.human_approval import human_approval
from nodes.send_response import send_response


def route_after_risk(state: AgentState) -> str:
    """
    This is the CONDITIONAL EDGE function from Step 1's design.
    LangGraph calls this after risk_evaluation runs, and whatever
    string it returns tells LangGraph which node to go to next.
    """
    if state["risk_flag"] == "high":
        return "human_approval"
    else:
        return "send_response"


def build_graph():
    """
    Builds and returns an UNCOMPILED graph (a 'builder'). We compile
    it separately (in run_agent.py / resume_agent.py) so we can attach
    a checkpointer at that point -- keeping this file focused purely
    on structure: nodes and edges.
    """
    builder = StateGraph(AgentState)

    # --- Register all 10 nodes ---
    builder.add_node("classify_email", classify_email)
    builder.add_node("understand_problem", understand_problem)
    builder.add_node("search_crm", search_crm)
    builder.add_node("search_knowledge_base", search_knowledge_base)
    builder.add_node("determine_resolution", determine_resolution)
    builder.add_node("create_ticket", create_ticket)
    builder.add_node("draft_response", draft_response)
    builder.add_node("risk_evaluation", risk_evaluation)
    builder.add_node("human_approval", human_approval)
    builder.add_node("send_response", send_response)

    # --- Straight-line edges (the fixed part of the pipeline) ---
    builder.add_edge(START, "classify_email")
    builder.add_edge("classify_email", "understand_problem")
    builder.add_edge("understand_problem", "search_crm")
    builder.add_edge("search_crm", "search_knowledge_base")
    builder.add_edge("search_knowledge_base", "determine_resolution")
    builder.add_edge("determine_resolution", "create_ticket")
    builder.add_edge("create_ticket", "draft_response")
    builder.add_edge("draft_response", "risk_evaluation")

    # --- The conditional branch (the ONE decision point in the graph) ---
    # After risk_evaluation, LangGraph calls route_after_risk(state).
    # Whatever node-name it returns is where execution goes next.
    builder.add_conditional_edges(
        "risk_evaluation",
        route_after_risk,
        {
            "human_approval": "human_approval",
            "send_response": "send_response",
        },
    )

    # Both paths eventually reach send_response, then END
    builder.add_edge("human_approval", "send_response")
    builder.add_edge("send_response", END)

    return builder