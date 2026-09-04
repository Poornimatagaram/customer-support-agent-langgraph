"""
Quick manual test for the risk_evaluation node.
Tests multiple scenarios to confirm the rules work correctly.
"""

from nodes.risk_evaluation import risk_evaluation

# Test 1: small refund, active account -> should be LOW risk
low_risk_state = {
    "resolution_plan": "Action: full_refund | Amount: $15.0 | Justification: small duplicate charge",
    "customer_data": {"account_status": "active"},
}
print("--- Test 1: small refund, active account ---")
print(risk_evaluation(low_risk_state))

# Test 2: large refund -> should be HIGH risk
high_risk_state = {
    "resolution_plan": "Action: full_refund | Amount: $89.99 | Justification: duplicate charge",
    "customer_data": {"account_status": "active"},
}
print("\n--- Test 2: refund over $50 ---")
print(risk_evaluation(high_risk_state))

# Test 3: flagged account -> should be HIGH risk regardless of amount
flagged_state = {
    "resolution_plan": "Action: full_refund | Amount: $10.0 | Justification: small refund",
    "customer_data": {"account_status": "flagged"},
}
print("\n--- Test 3: flagged account ---")
print(risk_evaluation(flagged_state))