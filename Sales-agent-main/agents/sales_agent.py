# agents/sales_agent.py
from datetime import datetime, timedelta
from typing import List, Dict, Any
import time
import re
import google.generativeai as genai
from config import GEMINI_API_KEY

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
GEMINI_MODEL = "gemini-2.0-flash-exp"  # Latest fast model

def filter_due_within(rfps: List[Dict[str, Any]], days:int=90) -> List[Dict[str, Any]]:
    now = datetime.now().date()
    limit = now + timedelta(days=days)
    candidates = []
    for r in rfps:
        due = r.get("due_date")
        try:
            if due:
                due_date = datetime.fromisoformat(due).date()
                if now <= due_date <= limit:
                    candidates.append(r)
            else:
                # If no due-date, optionally include as candidate (comment/uncomment)
                # candidates.append(r)
                pass
        except Exception:
            pass
    return candidates

def summarize_with_model(text: str) -> str:
    prompt = "Summarize this RFP in 2-3 concise bullet points, focusing on required products/services and acceptance/testing requirements:\n\n" + text
    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"⚠️ Gemini API error: {e}")
        # fallback: return trimmed text
        return text[:800]

def summarize_rfps(rfps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    summaries = []
    for r in rfps:
        text = f"Title: {r.get('title')}\n\n{r.get('description')}\n\nLink: {r.get('link')}"
        summary = summarize_with_model(text)
        summaries.append({**r, "summary": summary})
        time.sleep(0.6)  # polite pacing
    return summaries

def select_best_rfp(summaries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Use a short heuristic + model scoring to select the best RFP.
    Heuristic: earliest due-date wins; tie-breaker: ask model to pick.
    """
    if not summaries:
        return None
    # filter items that have due_date
    with_dates = [s for s in summaries if s.get("due_date")]
    if with_dates:
        sorted_by_due = sorted(with_dates, key=lambda x: x["due_date"])
        earliest = sorted_by_due[0]
        # Use model to confirm choice among top 3
        top_candidates = sorted_by_due[:3]
    else:
        # fallback to first 3
        top_candidates = summaries[:3]
        earliest = top_candidates[0]

    # Ask model to pick best among top_candidates
    prompt_text = "You are an assistant. Given these RFP summaries, pick the single best RFP for our company to respond to (brief reason):\n\n"
    for idx, c in enumerate(top_candidates, 1):
        prompt_text += f"{idx}. Title: {c['title']}\nDue: {c.get('due_date')}\nSummary: {c.get('summary')[:500]}\n\n"
    prompt_text += "\nRespond with the number of the chosen RFP and one short sentence explaining why."

    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(prompt_text)
        resp = response.text
        # try to parse leading number
        m = re.search(r"\b([1-9])\b", resp)
        if m:
            choice = int(m.group(1))
            chosen = top_candidates[choice-1]
            chosen['selection_reason'] = resp.strip()
            return chosen
    except Exception as e:
        print(f"⚠️ Gemini API error: {e}")
        pass

    # fallback to earliest
    earliest['selection_reason'] = "Selected by earliest due date (fallback)."
    return earliest
