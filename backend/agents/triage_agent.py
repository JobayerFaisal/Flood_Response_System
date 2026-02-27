# backend/agents/triage_agent.py
# Triage Agent

def triage_agent(state):

    triaged = []

    for r in state.reports:
        priority_score = (
            r["urgency"] * 0.6 +
            r["credibility"] * 0.4
        )

        r["priority_score"] = priority_score
        r["high_priority"] = priority_score >= 3.5

        triaged.append(r)

    state.triaged_reports = triaged
    return state
