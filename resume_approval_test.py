"""
resume_approval_test.py

Reconnects to the SAME checkpoint database and thread_id used by
start_approval_test.py, and resumes execution by supplying a human
decision via Command(resume=...). This proves the pause survived
across two completely separate script runs.
"""

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command

from nodes.state import AgentState
from nodes.human_approval import human_approval

# Rebuild the SAME graph structure (LangGraph needs the graph defined
# again in this new script -- but the checkpointer file itself is
# what actually remembers the state, not this Python code)
builder = StateGraph(AgentState)
builder.add_node("human_approval", human_approval)
builder.add_edge(START, "human_approval")
builder.add_edge("human_approval", END)

with SqliteSaver.from_conn_string("data/checkpoints.sqlite") as checkpointer:
    graph = builder.compile(checkpointer=checkpointer)

    # SAME thread_id as before -- this is how LangGraph finds the
    # correct paused conversation to resume.
    config = {"configurable": {"thread_id": "test-thread-001"}}

    # This is the human's decision -- imagine this coming from a
    # real approval UI. Command(resume=...) feeds this value back
    # in as the return value of the interrupt() call that paused things.
    human_decision = {
        "approved": True,
        "edited_reply": None,   # None means "use the original draft as-is"
    }

    result = graph.invoke(Command(resume=human_decision), config=config)

    print("\n--- Graph resumed and completed ---")
    print(result)