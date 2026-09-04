"""
Quick manual test for the draft_response node.
"""

from nodes.draft_response import draft_response

sample_state = {
    "issue_summary": "Request: refund for duplicate charge on order #4521 | Tone: frustrated",
    "resolution_plan": "Action: full_refund | Amount: $89.99 | Justification: duplicate charge treated as billing error, refunded in full",
    "customer_data": {
        "name": "Priya Sharma",
    },
}

result = draft_response(sample_state)

print("\n--- Node output ---")
print(result["draft_reply"])