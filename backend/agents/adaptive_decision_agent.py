# backend/agents/llm_decision_engine.py

import json
from backend.planning.llm_sitrep import generate_llm_sitrep


def generate_decision(context: dict):

    prompt_data = {
        "instruction": "You are a disaster coordination AI. "
                       "Based on the mission failure context, decide the next best action.",
        "context": context,
        "required_output_format": {
            "reasoning": "string explanation",
            "decision": {
                "action": "REASSIGN | ESCALATE | ABORT",
                "priority_adjustment": "NONE | INCREASE | CRITICAL",
                "additional_resources": "true/false"
            }
        }
    }

    response_text = generate_llm_sitrep(prompt_data)

    try:
        decision_json = json.loads(response_text)
        return decision_json
    except Exception:
        return {
            "reasoning": "Invalid LLM response. Fallback to safe policy.",
            "decision": {
                "action": "ESCALATE",
                "priority_adjustment": "CRITICAL",
                "additional_resources": True
            }
        }