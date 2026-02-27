# Medical Agent
# backend/agents/medical_agent.py

def medical_agent(state):

    flags = []

    for r in state.triaged_reports:
        if r["need_type"] == "medical" and r["urgency"] >= 4:
            flags.append({
                "report_id": r["report_id"],
                "priority": "critical"
            })

    state.medical_flags = flags
    return state