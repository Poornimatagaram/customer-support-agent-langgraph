"""
api.py

FastAPI wrapper around the LangGraph customer support agent.

Two main endpoints:
- POST /process-email : submit a new customer email
- POST /approve       : approve/reject a paused (high-risk) response

Uses a connection POOL (not a single connection) since a real API
serves many requests concurrently -- a pool manages multiple database
connections efficiently, reusing them across requests.
"""

from config_check import validate_config
validate_config()

import os
import uuid
from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.types import Command

from main import build_graph

app = FastAPI(title="Customer Support Agent API")

# Created ONCE when the API starts, reused across every request.
pool = ConnectionPool(
    conninfo=os.getenv("DATABASE_URL"),
    max_size=10,
    kwargs={"autocommit": True, "row_factory": dict_row},
)
checkpointer = PostgresSaver(pool)
builder = build_graph()
graph = builder.compile(checkpointer=checkpointer)


# --- Request/response shapes, validated automatically by FastAPI ---

class ProcessEmailRequest(BaseModel):
    email_text: str
    customer_id: str


class ApprovalRequest(BaseModel):
    thread_id: str
    approved: bool
    edited_reply: Optional[str] = None


@app.get("/health")
def health():
    """Simple endpoint to confirm the API is alive -- useful for
    deployment platforms to check the service is running correctly."""
    return {"status": "ok"}


@app.post("/process-email")
def process_email(request: ProcessEmailRequest):
    thread_id = f"email-{uuid.uuid4().hex[:8]}"
    config = {"configurable": {"thread_id": thread_id}}

    initial_state = {
        "email_text": request.email_text,
        "customer_id": request.customer_id,
    }

    result = graph.invoke(initial_state, config=config)

    # The reliable way to check if the graph is paused: ask for its
    # current state snapshot. snapshot.next is a non-empty tuple of
    # node names still waiting to run if we're paused; empty if done.
    snapshot = graph.get_state(config)

    if snapshot.next:
        # We're paused. snapshot.tasks holds info about the pending
        # node, including any interrupt() payloads it raised.
        interrupts = snapshot.tasks[0].interrupts if snapshot.tasks else ()
        approval_request = interrupts[0].value if interrupts else None

        return {
            "status": "pending_approval",
            "thread_id": thread_id,
            "approval_request": approval_request,
        }
    else:
        return {
            "status": "completed",
            "thread_id": thread_id,
            "result": result,
        }

@app.post("/approve")
def approve(request: ApprovalRequest):
    config = {"configurable": {"thread_id": request.thread_id}}

    human_decision = {
        "approved": request.approved,
        "edited_reply": request.edited_reply,
    }

    result = graph.invoke(Command(resume=human_decision), config=config)

    return {
        "status": "completed",
        "thread_id": request.thread_id,
        "result": result,
    }