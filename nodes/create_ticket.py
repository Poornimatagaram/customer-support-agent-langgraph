"""
Node: create_ticket

Logs a permanent ticket record into our SQLite database, capturing
the customer's issue and the agent's proposed resolution.

Like search_crm, this is a pure "tool" node -- no LLM call, just a
database write.
"""

import sqlite3
import uuid

from nodes.state import AgentState


def create_ticket(state: AgentState) -> AgentState:
    customer_id = state["customer_id"]
    category = state.get("category")
    issue_summary = state.get("issue_summary")
    resolution_plan = state.get("resolution_plan")

    # Generate a unique ticket ID. uuid4() creates a random, essentially
    # guaranteed-unique identifier -- standard practice for IDs you
    # don't want to accidentally collide/duplicate.
    ticket_id = f"TCKT-{uuid.uuid4().hex[:8].upper()}"

    conn = sqlite3.connect("data/crm.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO tickets (ticket_id, customer_id, category, issue_summary, resolution_plan)
        VALUES (?, ?, ?, ?, ?)
    """, (ticket_id, customer_id, category, issue_summary, resolution_plan))

    conn.commit()
    conn.close()

    print(f"[create_ticket] Created ticket {ticket_id} for customer {customer_id}")

    return {
        "ticket_id": ticket_id,
    }