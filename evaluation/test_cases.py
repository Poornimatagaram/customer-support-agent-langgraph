"""
test_cases.py

A set of realistic customer emails paired with EXPECTED outcomes,
based on our seeded CRM data and policy documents. This is our
"ground truth" -- what a correct agent SHOULD decide -- so we can
measure actual accuracy, not just eyeball individual runs.
"""

TEST_CASES = [
    {
        "name": "duplicate_charge_high_value",
        "email_text": "Hi, I was charged twice for my last order #4521. Please refund the extra charge ASAP, this is really frustrating.",
        "customer_id": "cust_001",   # Priya Sharma, order_amount=89.99, active
        "expected_category": "refund",
        "expected_risk_flag": "high",   # $89.99 > $50 threshold
    },
    {
        "name": "small_overcharge",
        "email_text": "Hi, I was charged $12 extra by mistake on my last order #4523. Could you please refund it?",
        "customer_id": "cust_003",   # Aiko Tanaka, order_amount=15.00, active
        "expected_category": "refund",
        "expected_risk_flag": "low",   # small amount, active account
    },
    {
        "name": "flagged_account_refund",
        "email_text": "I need a refund for my order #4524, I was overcharged.",
        "customer_id": "cust_004",   # Carlos Diaz, order_amount=500.00, FLAGGED
        "expected_category": "refund",
        "expected_risk_flag": "high",   # flagged account -> always high, regardless of amount
    },
    {
        "name": "account_deletion_request",
        "email_text": "I would like to permanently delete my account and all my data. Please process this as soon as possible.",
        "customer_id": "cust_002",   # James Miller, active
        "expected_category": "account",
        "expected_risk_flag": "low",
    },
    {
        "name": "general_shipping_question",
        "email_text": "Hi, my order was marked as delivered but I never received it. It's been 3 days. What should I do?",
        "customer_id": "cust_002",
        "expected_category": "general",
        "expected_risk_flag": "low",
    },
]
