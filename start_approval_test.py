"""
start_approval_test.py

Builds a tiny one-node LangGraph graph (just human_approval) with a
SQLite checkpointer, and runs it. It will hit interrupt() and PAUSE --
this script will print the interrupt payload and then EXIT COMPLETELY.

Run resume_approval_test.py afterward (in a separate command) to
prove the pause survived across two totally separate script runs.
"""

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver

from nodes.state import AgentState
from nodes.human_approval import human_approval

# --- Build a minimal graph with just one node ---
builder = StateGraph(AgentState)
builder.add_node("human_approval", human_approval)
builder.add_edge(START, "human_approval")
builder.add_edge("human_approval", END)

# The checkpointer -- saves every step's state into this SQLite file
with SqliteSaver.from_conn_string("data/checkpoints.sqlite") as checkpointer:
    graph = builder.compile(checkpointer=checkpointer)

    # thread_id uniquely identifies THIS paused conversation, so we
    # can resume the correct one later, even among many.
    config = {"configurable": {"thread_id": "test-thread-001"}}

    initial_state = {
        "draft_reply": "Hi Priya, we've processed a full refund of $89.99 for your duplicate charge.",
        "risk_flag": "high",
    }

    result = graph.invoke(initial_state, config=config)

    print("\n--- Graph paused (interrupted) ---")
    print(result)
    print("\nThis script is now exiting completely.")
    print("Run resume_approval_test.py separately to continue from here.")