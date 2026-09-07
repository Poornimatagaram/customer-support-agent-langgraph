"""
Node: create_ticket

Logs a permanent ticket record into our Postgres database.
"""

import os
import uuid
from dotenv import load_dotenv
import psycopg2

from nodes.state import AgentState

load_dotenv()


def create_ticket(state: AgentState) -> AgentState:
    customer_id = state["customer_id"]
    category = state.get("category")
    issue_summary = state.get("issue_summary")
    resolution_plan = state.get("resolution_plan")

    ticket_id = f"TCKT-{uuid.uuid4().hex[:8].upper()}"

    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO tickets (ticket_id, customer_id, category, issue_summary, resolution_plan)
        VALUES (%s, %s, %s, %s, %s)
    """, (ticket_id, customer_id, category, issue_summary, resolution_plan))

    conn.commit()
    cursor.close()
    conn.close()

    print(f"[create_ticket] Created ticket {ticket_id} for customer {customer_id}")

    return {
        "ticket_id": ticket_id,
    }