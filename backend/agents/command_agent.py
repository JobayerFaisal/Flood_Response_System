# Command Agent
# backend/agents/command_agent.py

from backend.agents.rag import retrieve_relevant_knowledge


def command_agent(state):

    retrieved_knowledge = retrieve_relevant_knowledge(state)

    state.final_plan = {
        "severity": state.flood_event["severity"],
        "clusters": state.clusters,
        "allocation": state.allocation_plan,
        "routes": state.routes,
        "medical_cases": state.medical_flags,
        "knowledge_references": retrieved_knowledge
    }

    return state