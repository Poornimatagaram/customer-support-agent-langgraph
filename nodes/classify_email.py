"""
Node: classify_email

Reads the raw customer email and asks Gemini to classify it into
a category and urgency level. Writes results back into state.
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


class ClassificationResult(BaseModel):
    category: Literal["billing", "technical", "refund", "account", "general"]
    urgency: Literal["low", "medium", "high"]
    reasoning: str


@retry(
    stop=stop_after_attempt(3),                              # give up after 3 total tries
    wait=wait_exponential(multiplier=1, min=2, max=20),      # wait 2s, then 4s, then 8s... capped at 20s
    retry=retry_if_exception_type((ResourceExhausted, ServiceUnavailable)),  # ONLY retry these specific errors
)
def _call_gemini(prompt: str):
    """
    Isolating the actual API call into its own small function is what
    lets us cleanly attach @retry to just this part -- not the whole
    node -- so parsing/validation errors (which retrying won't fix)
    don't get endlessly retried too.
    """
    model = genai.GenerativeModel(MODEL_NAME)
    return model.generate_content(prompt)


def classify_email(state: AgentState) -> AgentState:
    email_text = state["email_text"]

    prompt = f"""You are a customer support triage assistant.

Classify the following customer email.

Email:
\"\"\"{email_text}\"\"\"

Respond ONLY with valid JSON in this exact shape, no other text:
{{
  "category": "billing" | "technical" | "refund" | "account" | "general",
  "urgency": "low" | "medium" | "high",
  "reasoning": "one short sentence explaining why"
}}
"""

    try:
        response = _call_gemini(prompt)
        raw_text = response.text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        parsed = ClassificationResult.model_validate(json.loads(raw_text))

        print(f"[classify_email] category={parsed.category} urgency={parsed.urgency} | {parsed.reasoning}")

        return {
            "category": parsed.category,
            "urgency": parsed.urgency,
        }

    except Exception as e:
        # If classification fails even after retries, we don't want to
        # crash the whole pipeline. Fall back to a safe default that
        # routes this case toward human review instead.
        print(f"[classify_email] ERROR after retries: {e}. Falling back to 'general'/'high' for safety.")
        return {
            "category": "general",
            "urgency": "high",
        }