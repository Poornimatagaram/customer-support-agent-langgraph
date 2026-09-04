"""
Node: draft_response

Takes the resolution decision and writes an actual customer-facing
email reply -- professional tone, clearly stating what will happen.

Unlike earlier nodes, this doesn't need Pydantic/JSON structure --
the output IS the final text (an email), not a decision to parse.
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

from nodes.state import AgentState

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

MODEL_NAME = "gemini-3.6-flash"


def draft_response(state: AgentState) -> AgentState:
    issue_summary = state["issue_summary"]
    resolution_plan = state["resolution_plan"]
    customer_data = state.get("customer_data", {})
    customer_name = customer_data.get("name", "there") if customer_data else "there"

    prompt = f"""You are a customer support agent writing a reply email.

Customer's name: {customer_name}
Customer's issue: {issue_summary}
Decided resolution: {resolution_plan}

Write a short, warm, professional email reply to the customer that:
- Acknowledges their issue with empathy
- Clearly states what action is being taken (based on the resolution above)
- Does NOT invent any details not present in the resolution
- Signs off as "Customer Support Team"

Write ONLY the email body text, no subject line, no explanation, no markdown formatting.
"""

    model = genai.GenerativeModel(MODEL_NAME)
    response = model.generate_content(prompt)

    draft_reply = response.text.strip()

    print(f"[draft_response] Draft generated ({len(draft_reply)} characters)")

    return {
        "draft_reply": draft_reply,
    }