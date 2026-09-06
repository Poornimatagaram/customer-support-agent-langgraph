"""
resume_agent.py

Resumes a paused graph run, given its thread_id (printed by run_agent.py
when it paused). Takes the thread_id as a command-line argument.

Usage: python3 resume_agent.py <thread_id>
"""

import sys

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command

from main import build_graph

if len(sys.argv) < 2:
    print("Usage: python3 resume_agent.py <thread_id>")
    sys.exit(1)

thread_id = sys.argv[1]

with SqliteSaver.from_conn_string("data/checkpoints.sqlite") as checkpointer:
    builder = build_graph()
    graph = builder.compile(checkpointer=checkpointer)

    config = {"configurable": {"thread_id": thread_id}}

    # Simulating a human reviewer approving the draft as-is.
    # In a real UI, this would come from a button click / form submission.
    human_decision = {
        "approved": True,
        "edited_reply": None,
    }

    print(f"Resuming thread_id = {thread_id} with decision: {human_decision}\n")

    result = graph.invoke(Command(resume=human_decision), config=config)

    print("\n--- Final state after resume ---")
    print(result)
    print(f"\nsent_status: {result.get('sent_status')}")