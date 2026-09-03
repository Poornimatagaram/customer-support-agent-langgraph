"""
Quick manual test for the determine_resolution node.

Notice this state combines outputs from THREE earlier nodes
(understand_problem, search_crm, search_knowledge_base) --
this is what the real graph will do automatically once wired together.
"""

from nodes.determine_resolution import determine_resolution

sample_state = {
    "issue_summary": "Request: The customer is requesting a refund for a duplicate charge on their order. | Details: Order number: #4521, issue: charged twice | Tone: frustrated",
    "customer_data": {
        "found": True,
        "customer_id": "cust_001",
        "name": "Priya Sharma",
        "email": "priya@example.com",
        "order_id": "4521",
        "order_amount": 89.99,
        "order_date": "2026-08-15",
        "account_status": "active",
    },
    "retrieved_docs": [
        "For orders over $200, refund requests must be reviewed by a support specialist before processing. Digital products and gift cards are non-refundable once redeemed. If a customer was charged twice for the same order (a duplicate charge), this is treated as a billing error and should be refunded in full without requiring the customer to return any item.",
        "Customers are eligible for a full refund within 30 days of purchase if the item is unused and in original packaging. Refunds for duplicate or accidental charges are processed automatically once verified and typically take 3-5 business days to appear on the customer's statement.",
    ],
}

result = determine_resolution(sample_state)

print("\n--- Node output ---")
print(result)