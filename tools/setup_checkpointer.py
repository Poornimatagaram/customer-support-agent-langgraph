"""
setup_checkpointer.py

One-time setup: creates the internal tables LangGraph's Postgres
checkpointer needs to store paused/resumable graph state.
Run this ONCE before using PostgresSaver anywhere else.
"""

import os
from dotenv import load_dotenv
from langgraph.checkpoint.postgres import PostgresSaver

load_dotenv()

with PostgresSaver.from_conn_string(os.getenv("DATABASE_URL")) as checkpointer:
    checkpointer.setup()

print("Postgres checkpointer tables created.")