# agents/response_agent.py
import google.generativeai as genai
from config import GEMINI_API_KEY

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
GEMINI_MODEL = "gemini-2.0-flash-exp"

def generate_draft_response(rfp: dict) -> str:
    prompt = f"""You are a professional sales proposal writer for an FMCG supplier.
Given the RFP below, generate a concise cover response (2-3 paragraphs) that:
- Acknowledges the RFP
- Summarizes why our company is a fit
- Mentions key delivery/testing/acceptance highlights

RFP Title: {rfp.get('title')}
Due: {rfp.get('due_date')}
Summary: {rfp.get('summary')}

Write the response as a formal email body (no signatures)."""
    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"⚠️ Gemini API error: {e}")
        return f"Draft fallback: We can respond to this RFP. Details: {rfp.get('summary')[:600]}"
