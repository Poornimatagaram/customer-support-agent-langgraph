"""
Quick manual test for the send_response node.
Tests both the low-risk (no edited_reply) and high-risk (edited_reply set) paths.
"""

from nodes.send_response import send_response

# Low-risk path: never went through human_approval
low_risk_state = {
    "draft_reply": "Hi, your refund has been processed automatically.",
}
print("--- Test 1: low-risk path (no edited_reply) ---")
print(send_response(low_risk_state))

# High-risk path: went through human_approval
high_risk_state = {
    "draft_reply": "Hi, your refund has been processed automatically.",
    "edited_reply": "Hi, I've personally reviewed and approved your refund.",
}
print("\n--- Test 2: high-risk path (edited_reply present) ---")
print(send_response(high_risk_state))