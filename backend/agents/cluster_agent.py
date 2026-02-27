# backend/agents/cluster_agent.py
# Cluster Agent 

from backend.planning.clustering import cluster_reports
from backend.planning.resource_allocation import estimate_cluster_demand


def cluster_agent(state):

    clustered = cluster_reports(state.triaged_reports)
    demand = estimate_cluster_demand(clustered)

    state.clusters = demand
    state.triaged_reports = clustered

    return state