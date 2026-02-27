# Resource Agent
# backend/agents/resource_agent.py

from backend.planning.fair_allocation import fair_allocate_boats


def resource_agent(state):

    cluster_urgency = {
        cid: sum(r["urgency"] for r in state.triaged_reports if r["cluster_id"] == cid)
        for cid in state.clusters
    }

    allocation = fair_allocate_boats(
        state.clusters,
        cluster_urgency,
        boat_count=3,
        boat_capacity=50
    )

    state.allocation_plan = allocation
    return state