"""
Node: determine_resolution

The core decision-making step. Combines:
- issue_summary (from understand_problem)
- customer_data (from search_crm)
- retrieved_docs (from search_knowledge_base -- the RAG context)

...and asks the LLM to decide what action to take, grounded in real
policy text and real customer data. This is the "Generation" half of RAG.
"""

import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
from pydantic import BaseModel
from typing import Literal

from nodes.state import AgentState

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

MODEL_NAME = "gemini-3.6-flash"


class ResolutionDecision(BaseModel):
    action: Literal["full_refund", "partial_refund", "replace_item", "answer_question", "escalate_to_human"]
    justification: str      # which policy/fact this decision is based on -- for traceability
    refund_amount: float    # 0 if no refund applies


def determine_resolution(state: AgentState) -> AgentState:
    issue_summary = state["issue_summary"]
    customer_data = state["customer_data"]
    retrieved_docs = state["retrieved_docs"]

    # Join the retrieved chunks into one block of text for the prompt.
    # This is the "augmentation" step of RAG -- inserting retrieved
    # context directly into what the LLM sees.
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

    model = genai.GenerativeModel(MODEL_NAME)
    response = model.generate_content(prompt)

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