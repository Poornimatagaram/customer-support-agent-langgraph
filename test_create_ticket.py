"""
Quick manual test for the create_ticket node.
"""

from nodes.create_ticket import create_ticket

sample_state = {
    "customer_id": "cust_001",
    "category": "refund",
    "issue_summary": "Request: refund for duplicate charge on order #4521",
    "resolution_plan": "Action: full_refund | Amount: $89.99 | Justification: duplicate charge billing error",
}

result = create_ticket(sample_state)

print("\n--- Node output ---")
print(result)