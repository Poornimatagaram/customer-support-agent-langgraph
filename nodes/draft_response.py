"""
Node: draft_response

Takes the resolution decision and writes an actual customer-facing
email reply.
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from google.api_core.exceptions import ResourceExhausted, ServiceUnavailable

from nodes.state import AgentState

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=20),
    retry=retry_if_exception_type((ResourceExhausted, ServiceUnavailable)),
)
def _call_gemini(prompt: str):
    model = genai.GenerativeModel(MODEL_NAME)
    return model.generate_content(prompt)


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

    try:
        response = _call_gemini(prompt)
        draft_reply = response.text.strip()

        print(f"[draft_response] Draft generated ({len(draft_reply)} characters)")

        return {
            "draft_reply": draft_reply,
        }

    except Exception as e:
        print(f"[draft_response] ERROR after retries: {e}. Using generic fallback template.")
        return {
            "draft_reply": f"Dear {customer_name},\n\nThank you for contacting us. Our team is reviewing your request and will follow up shortly with next steps.\n\nWarm regards,\nCustomer Support Team",
        }