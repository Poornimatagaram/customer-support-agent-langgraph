"""
run_agent.py

Runs a real customer email through the ENTIRE 10-node graph, end to end.

If the email is LOW risk: the graph completes fully in one call.
If the email is HIGH risk: the graph will pause at human_approval --
this script will print the interrupt payload and exit. Use
resume_agent.py (built next) to supply the human decision and finish.
"""
from dotenv import load_dotenv
load_dotenv()
import sys
import uuid

from langgraph.checkpoint.sqlite import SqliteSaver

from main import build_graph

# A fresh, unique thread_id per email -- this is what lets many
# different customer emails be paused/tracked independently.
THREAD_ID = f"email-{uuid.uuid4().hex[:8]}"

with SqliteSaver.from_conn_string("data/checkpoints.sqlite") as checkpointer:
    builder = build_graph()
    graph = builder.compile(checkpointer=checkpointer)

    config = {"configurable": {"thread_id": THREAD_ID}}

    #initial_state = {
       # "email_text": "Hi, I was charged twice for my last order #4521. Please refund the extra charge ASAP, this is really frustrating.",
        #"customer_id": "cust_001",
    #}

    initial_state = {
        "email_text": "Hi, I was charged $12 extra by mistake on my last order #4523. Could you please refund it?",
        "customer_id": "cust_003",
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