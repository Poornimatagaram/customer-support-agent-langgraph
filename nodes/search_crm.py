"""
Node: search_crm

Looks up the customer's record in our mock CRM database (SQLite),
using the customer_id already present in state.

Unlike classify_email and understand_problem, this node does NOT call
the LLM at all -- it's a pure "tool" node: it just fetches real data.
"""

import sqlite3

from nodes.state import AgentState


def search_crm(state: AgentState) -> AgentState:
    customer_id = state["customer_id"]

    # Connect to the same database file seed_crm.py created
    conn = sqlite3.connect("data/crm.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM customers WHERE customer_id = ?", (customer_id,))
    row = cursor.fetchone()

    conn.close()

    if row is None:
        # Customer not found -- still need to return SOMETHING sensible,
        # not crash. Downstream nodes should handle this gracefully.
        print(f"[search_crm] No customer found for id={customer_id}")
        customer_data = {"found": False}
    else:
        # row is a tuple in column order: matches our CREATE TABLE column order
        customer_data = {
            "found": True,
            "customer_id": row[0],
            "name": row[1],
            "email": row[2],
            "order_id": row[3],
            "order_amount": row[4],
            "order_date": row[5],
            "account_status": row[6],
        }
        print(f"[search_crm] Found customer: {customer_data['name']} ({customer_data['account_status']})")

    return {
        "customer_data": customer_data,
    }