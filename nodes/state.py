"""
State schema for the Customer Ops Agent.

This is the "shared notebook" that every node in the LangGraph reads from
and writes to. Each field maps to something a node produces or needs,
based on our Step 1 workflow design.
"""

from typing import TypedDict, Optional


class AgentState(TypedDict):
    # --- Input ---
    email_text: str            # raw incoming customer email
    customer_id: str           # who sent it (in a real system, parsed from the email address)

    # --- classify_email node ---
    category: Optional[str]    # e.g. "billing", "technical", "refund", "general"
    urgency: Optional[str]     # e.g. "low", "medium", "high"

    # --- understand_problem node ---
    issue_summary: Optional[str]   # LLM's structured summary of what the customer wants

    # --- search_crm node ---
    customer_data: Optional[dict]  # customer's account/order history from our mock CRM

    # --- search_knowledge_base node ---
    retrieved_docs: Optional[list] # relevant policy/help doc snippets from RAG search

    # --- determine_resolution node ---
    resolution_plan: Optional[str] # what the agent has decided to do

    # --- create_ticket node ---
    ticket_id: Optional[str]

    # --- draft_response node ---
    draft_reply: Optional[str]

    # --- risk_evaluation node ---
    risk_flag: Optional[str]   # "low" or "high" -- drives the conditional edge

    # --- human_approval node ---
    approved: Optional[bool]
    edited_reply: Optional[str]    # in case the human edits the draft before sending

    # --- send_response node ---
    sent_status: Optional[str]