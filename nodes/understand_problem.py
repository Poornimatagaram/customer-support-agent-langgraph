"""
Node: understand_problem

Takes the raw email + its category, and extracts a clean, structured
understanding of what the customer actually wants -- separating the
real request from venting/pleasantries/irrelevant details.

This runs AFTER classify_email, because it uses `category` from state.
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


class ProblemUnderstanding(BaseModel):
    core_request: str
    key_details: str
    customer_tone: Literal["neutral", "frustrated", "angry", "confused"]


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=20),
    retry=retry_if_exception_type((ResourceExhausted, ServiceUnavailable)),
)
def _call_gemini(prompt: str):
    model = genai.GenerativeModel(MODEL_NAME)
    return model.generate_content(prompt)


def understand_problem(state: AgentState) -> AgentState:
    email_text = state["email_text"]
    category = state["category"]

    prompt = f"""You are a customer support analyst.

The following email has already been categorized as: "{category}"

Email:
\"\"\"{email_text}\"\"\"

Extract a clean, structured understanding of the customer's request.
Separate the actual actionable request from emotional venting or pleasantries.

Respond ONLY with valid JSON in this exact shape, no other text:
{{
  "core_request": "one clear sentence describing what the customer wants done",
  "key_details": "concrete facts: order numbers, dates, amounts, etc. 'none' if none present",
  "customer_tone": "neutral" | "frustrated" | "angry" | "confused"
}}
"""

    try:
        response = _call_gemini(prompt)
        raw_text = response.text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        parsed = ProblemUnderstanding.model_validate(json.loads(raw_text))

        issue_summary = (
            f"Request: {parsed.core_request} | "
            f"Details: {parsed.key_details} | "
            f"Tone: {parsed.customer_tone}"
        )

        print(f"[understand_problem] {issue_summary}")

        return {
            "issue_summary": issue_summary,
        }

    except Exception as e:
        # Fallback: use the raw email text itself as the "summary" so
        # downstream nodes still have SOMETHING to work with, rather
        # than a missing field that would break later prompts.
        print(f"[understand_problem] ERROR after retries: {e}. Falling back to raw email text.")
        return {
            "issue_summary": f"Request: (auto-extraction failed) raw email: {email_text} | Tone: unknown",
        }