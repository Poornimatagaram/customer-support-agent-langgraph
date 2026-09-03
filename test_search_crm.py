"""
Quick manual test for the search_crm node.
"""

from nodes.search_crm import search_crm

# Test 1: a customer that exists in our seeded data
sample_state = {
    "customer_id": "cust_001",
}

result = search_crm(sample_state)
print("\n--- Test 1: existing customer ---")
print(result)

# Test 2: a customer_id that does NOT exist -- testing our "not found" handling
sample_state_missing = {
    "customer_id": "cust_999",
}

result_missing = search_crm(sample_state_missing)
print("\n--- Test 2: missing customer ---")
print(result_missing)