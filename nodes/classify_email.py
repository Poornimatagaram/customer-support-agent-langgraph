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

from nodes.state import AgentState

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

MODEL_NAME = "gemini-3.6-flash"


class ClassificationResult(BaseModel):
    category: Literal["billing", "technical", "refund", "account", "general"]
    urgency: Literal["low", "medium", "high"]
    reasoning: str


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

    model = genai.GenerativeModel(MODEL_NAME)
    response = model.generate_content(prompt)

    raw_text = response.text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    parsed = ClassificationResult.model_validate(json.loads(raw_text))

    print(f"[classify_email] category={parsed.category} urgency={parsed.urgency} | {parsed.reasoning}")

    return {
        "category": parsed.category,
        "urgency": parsed.urgency,
    }