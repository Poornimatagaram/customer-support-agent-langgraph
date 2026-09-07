"""
resume_agent.py

Resumes a paused graph run, given its thread_id. Uses the same
explicit autocommit connection pattern as run_agent.py.
"""

import os
import sys

import psycopg
from psycopg.rows import dict_row
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.types import Command

from main import build_graph

if len(sys.argv) < 2:
    print("Usage: python3 resume_agent.py <thread_id>")
    sys.exit(1)

thread_id = sys.argv[1]

conn = psycopg.connect(
    os.getenv("DATABASE_URL"),
    autocommit=True,
    row_factory=dict_row,
)
checkpointer = PostgresSaver(conn)

builder = build_graph()
graph = builder.compile(checkpointer=checkpointer)

config = {"configurable": {"thread_id": thread_id}}

human_decision = {
    "approved": True,
    "edited_reply": None,
}

print(f"Resuming thread_id = {thread_id} with decision: {human_decision}\n")

result = graph.invoke(Command(resume=human_decision), config=config)

print("\n--- Final state after resume ---")
print(result)
print(f"\nsent_status: {result.get('sent_status')}")

conn.close()