"""
Quick manual test for the classify_email node.
Run this directly to see the node work in isolation, before
it's wired into the full graph.
"""

from nodes.classify_email import classify_email

# Fake starting state -- only the fields classify_email actually needs
sample_state = {
    "email_text": "Hi, I was charged twice for my last order #4521. Please refund the extra charge ASAP, this is really frustrating.",
    "customer_id": "cust_001",
}

result = classify_email(sample_state)

print("\n--- Node output ---")
print(result)