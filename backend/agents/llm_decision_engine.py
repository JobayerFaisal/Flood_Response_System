import json
from backend.planning.llm_sitrep import generate_llm_sitrep
from backend.agents.decision_scoring import compute_failure_risk_score
from backend.agents.rag import retrieve_decision_knowledge


def generate_decision(context: dict):

    risk_score = compute_failure_risk_score(context)
    retrieved_knowledge = retrieve_decision_knowledge(context)

    hybrid_input = {
        "context": context,
        "numeric_risk_score": risk_score,
        "retrieved_guidelines": retrieved_knowledge,
        "instruction": (
            "Based on risk score and guidelines, return structured JSON decision."
        ),
        "required_output_format": {
            "reasoning": "string",
            "decision": {
                "action": "REASSIGN | ESCALATE | ABORT",
                "priority_adjustment": "NONE | INCREASE | CRITICAL",
                "additional_resources": "true/false"
            }
        }
    }

    response_text = generate_llm_sitrep(hybrid_input)

    try:
        decision_json = json.loads(response_text)
        return decision_json
    except Exception:
        return {
            "reasoning": "Fallback: numeric risk exceeded threshold.",
            "decision": {
                "action": "ESCALATE" if risk_score > 12 else "REASSIGN",
                "priority_adjustment": "CRITICAL",
                "additional_resources": True
            }
        }