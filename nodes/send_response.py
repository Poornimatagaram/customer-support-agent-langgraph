"""
Node: send_response

The final step. In a real system, this would call an email API
(SendGrid, AWS SES, etc.). Here, it's mocked -- it just prints the
final approved reply and marks the state as sent.

Only reached if the customer was either auto-approved (low risk)
or explicitly approved by a human (high risk).
"""

from nodes.state import AgentState


def send_response(state: AgentState) -> AgentState:
    # Use the human-edited reply if one exists, otherwise the original draft.
    # This handles BOTH paths: low-risk (skipped human_approval entirely,
    # so edited_reply was never set) and high-risk (human may have edited it).
    final_reply = state.get("edited_reply") or state.get("draft_reply")

    print(f"[send_response] Sending email:\n---\n{final_reply}\n---")

    return {
        "sent_status": "sent",
    }