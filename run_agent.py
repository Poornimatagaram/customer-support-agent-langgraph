"""
run_agent.py

Runs a real customer email through the ENTIRE 10-node graph, end to end.
Explicitly creates the Postgres connection with autocommit=True to
ensure checkpoint writes are immediately durable, not left in an
uncommitted transaction.
"""

from config_check import validate_config
validate_config()

import os
import uuid

import psycopg
from psycopg.rows import dict_row
from langgraph.checkpoint.postgres import PostgresSaver

from main import build_graph

THREAD_ID = f"email-{uuid.uuid4().hex[:8]}"

conn = psycopg.connect(
    os.getenv("DATABASE_URL"),
    autocommit=True,
    row_factory=dict_row,
)
checkpointer = PostgresSaver(conn)

builder = build_graph()
graph = builder.compile(checkpointer=checkpointer)

config = {"configurable": {"thread_id": THREAD_ID}}

initial_state = {
    "email_text": "Hi, I was charged twice for my last order #4521. Please refund the extra charge ASAP, this is really frustrating.",
    "customer_id": "cust_001",
}

print(f"Starting graph run. thread_id = {THREAD_ID}\n")

result = graph.invoke(initial_state, config=config)

print("\n--- Final state ---")
print(result)

if result.get("sent_status") == "sent":
    print("\nEmail fully processed and sent -- no human approval was needed.")
else:
    print(f"\nGraph is PAUSED, waiting for human approval.")
    print(f"To resume, run: python3 resume_agent.py {THREAD_ID}")

conn.close()