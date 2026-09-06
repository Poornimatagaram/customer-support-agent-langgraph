"""
Node: determine_resolution

The core decision-making step. Combines issue_summary, customer_data,
and retrieved_docs (RAG context) to decide what action to take.
"""

import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
from pydantic import BaseModel
from typing import Literal
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from google.api_core.exceptions import ResourceExhausted, ServiceUnavailable

from nodes.state import AgentState

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")


class ResolutionDecision(BaseModel):
    action: Literal["full_refund", "partial_refund", "replace_item", "answer_question", "escalate_to_human"]
    justification: str
    refund_amount: float


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=20),
    retry=retry_if_exception_type((ResourceExhausted, ServiceUnavailable)),
)
def _call_gemini(prompt: str):
    model = genai.GenerativeModel(MODEL_NAME)
    return model.generate_content(prompt)


def determine_resolution(state: AgentState) -> AgentState:
    issue_summary = state["issue_summary"]
    customer_data = state["customer_data"]
    retrieved_docs = state["retrieved_docs"]

    policy_context = "\n\n".join(retrieved_docs)

    prompt = f"""You are a customer support decision-making assistant.

Customer issue:
{issue_summary}

Customer account data:
{json.dumps(customer_data)}

Relevant company policy excerpts:
{policy_context}

Based ONLY on the policy excerpts and customer data above, decide what
action should be taken. Do not invent policies not shown above.

Respond ONLY with valid JSON in this exact shape, no other text:
{{
  "action": "full_refund" | "partial_refund" | "replace_item" | "answer_question" | "escalate_to_human",
  "justification": "one sentence citing which policy or fact drove this decision",
  "refund_amount": <number, 0 if no refund applies>
}}
"""

    try:
        response = _call_gemini(prompt)
        raw_text = response.text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        parsed = ResolutionDecision.model_validate(json.loads(raw_text))

        resolution_plan = (
            f"Action: {parsed.action} | "
            f"Amount: ${parsed.refund_amount} | "
            f"Justification: {parsed.justification}"
        )

        print(f"[determine_resolution] {resolution_plan}")

        return {
            "resolution_plan": resolution_plan,
        }

    except Exception as e:
        print(f"[determine_resolution] ERROR after retries: {e}. Escalating to human for safety.")
        return {
            "resolution_plan": "Action: escalate_to_human | Amount: $0.0 | Justification: Automated decision failed, routing to human for manual review.",
        }