"""
Quick manual test for the understand_problem node.
"""

from nodes.understand_problem import understand_problem

sample_state = {
    "email_text": "Hi, I was charged twice for my last order #4521. Please refund the extra charge ASAP, this is really frustrating.",
    "customer_id": "cust_001",
    "category": "refund",
}

result = understand_problem(sample_state)

print("\n--- Node output ---")
print(result)