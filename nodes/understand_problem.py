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

from nodes.state import AgentState

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

MODEL_NAME = "gemini-3.6-flash"


class ProblemUnderstanding(BaseModel):
    core_request: str          # what the customer actually wants done, one clear sentence
    key_details: str           # order numbers, dates, amounts -- anything concrete to act on
    customer_tone: Literal["neutral", "frustrated", "angry", "confused"]


def understand_problem(state: AgentState) -> AgentState:
    email_text = state["email_text"]
    category = state["category"]   # <- depends on classify_email having already run

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

    model = genai.GenerativeModel(MODEL_NAME)
    response = model.generate_content(prompt)

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