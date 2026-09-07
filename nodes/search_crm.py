"""
Node: search_crm

Looks up the customer's record in our Postgres CRM database,
using the customer_id already present in state.
"""

import os
from dotenv import load_dotenv
import psycopg2

from nodes.state import AgentState

load_dotenv()


def search_crm(state: AgentState) -> AgentState:
    customer_id = state["customer_id"]

    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM customers WHERE customer_id = %s", (customer_id,))
    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if row is None:
        print(f"[search_crm] No customer found for id={customer_id}")
        customer_data = {"found": False}
    else:
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