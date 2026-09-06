"""
Node: human_approval

Pauses graph execution and waits for a human decision. Uses
LangGraph's interrupt() -- when called, execution freezes here,
state is saved via the checkpointer, and control returns to whoever
is running the graph. Later, a separate process can resume this
exact paused execution by supplying the human's decision.
"""

from langgraph.types import interrupt

from nodes.state import AgentState


def human_approval(state: AgentState) -> AgentState:
    draft_reply = state.get("draft_reply")
    risk_flag = state.get("risk_flag")

    # interrupt() pauses execution HERE. The dict we pass becomes the
    # payload a human reviewer sees. Whatever value is later passed
    # back via Command(resume=...) becomes the return value of this
    # interrupt() call, as if it had returned instantly.
    decision = interrupt({
        "message": "Human approval required before sending this response.",
        "risk_flag": risk_flag,
        "draft_reply": draft_reply,
    })

    approved = decision.get("approved", False)
    # If the human edited the reply, use their version; otherwise keep the draft
    edited_reply = decision.get("edited_reply") or draft_reply

    print(f"[human_approval] Human decision: approved={approved}")

    return {
        "approved": approved,
        "edited_reply": edited_reply,
    }