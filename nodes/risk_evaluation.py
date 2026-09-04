"""
Node: risk_evaluation

Deterministic (non-LLM) rule-based logic that decides whether this
resolution needs human approval before sending, or is safe to
auto-send. This is intentionally NOT an LLM call -- safety-critical
routing should be predictable and auditable, not probabilistic.

Sets risk_flag, which the graph's conditional edge will read to decide
whether to route to human_approval or straight to send_response.
"""

import re

from nodes.state import AgentState

REFUND_RISK_THRESHOLD = 50.0


def risk_evaluation(state: AgentState) -> AgentState:
    resolution_plan = state.get("resolution_plan", "")
    customer_data = state.get("customer_data", {}) or {}

    # --- Parse the refund amount back out of the resolution_plan string ---
    # resolution_plan looks like: "Action: full_refund | Amount: $89.99 | Justification: ..."
    # re.search with a regex pattern finds "Amount: $<number>" and captures the number.
    amount_match = re.search(r"Amount:\s*\$([\d.]+)", resolution_plan)
    refund_amount = float(amount_match.group(1)) if amount_match else 0.0

    action_match = re.search(r"Action:\s*(\w+)", resolution_plan)
    action = action_match.group(1) if action_match else "unknown"

    account_status = customer_data.get("account_status", "active")

    # --- Apply the deterministic risk rules ---
    reasons = []

    if refund_amount > REFUND_RISK_THRESHOLD:
        reasons.append(f"refund amount ${refund_amount} exceeds ${REFUND_RISK_THRESHOLD} threshold")

    if account_status == "flagged":
        reasons.append("customer account is flagged")

    if action == "escalate_to_human":
        reasons.append("resolution explicitly requested escalation")

    risk_flag = "high" if reasons else "low"

    print(f"[risk_evaluation] risk={risk_flag} | reasons={reasons if reasons else 'none'}")

    return {
        "risk_flag": risk_flag,
    }