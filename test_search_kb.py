"""
Quick manual test for the search_knowledge_base node.
"""

from nodes.search_knowledge_base import search_knowledge_base

sample_state = {
    "issue_summary": "Request: The customer is requesting a refund for a duplicate charge on their order. | Details: Order number: #4521, issue: charged twice | Tone: frustrated",
}

result = search_knowledge_base(sample_state)

print("\n--- Node output ---")
for doc in result["retrieved_docs"]:
    print(f"- {doc}\n")