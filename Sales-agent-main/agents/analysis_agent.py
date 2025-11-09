# agents/analysis_agent.py
import ollama

OLLAMA_MODEL = "llama3"

def refine_response(draft: str) -> str:
    prompt = (
        "You are a senior proposal reviewer. Improve the clarity, tone, and professional quality of the draft below. "
        "Keep it concise and correct grammar. If there are missing assumptions, add a short bullet list of assumptions at the end.\n\n"
        "Draft:\n" + draft
    )
    try:
        out = ollama.chat(model=OLLAMA_MODEL, messages=[{"role":"user","content":prompt}])
        return out['choices'][0]['message']['content']
    except Exception as e:
        return draft + "\n\n[Refinement failed: " + str(e) + "]"
