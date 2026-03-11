# backend/agents/decision_scoring.py

def compute_failure_risk_score(context: dict) -> float:

    score = 0

    severity = context.get("severity", 1)
    priority = context.get("priority", "MEDIUM")
    reason = context.get("reason", "")

    # Severity weight
    score += severity * 2

    # Priority weight
    if priority == "CRITICAL":
        score += 5
    elif priority == "HIGH":
        score += 3

    # Failure reason weight
    if "blocked" in reason.lower():
        score += 4

    if "medical" in reason.lower():
        score += 6

    return score