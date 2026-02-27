# Routing Agent
# backend/agents/routing_agent.py

from backend.planning.routing import (
    generate_grid_graph,
    block_roads_based_on_severity,
    find_route,
    latlon_to_grid,
)
from backend.planning.cluster_utils import compute_cluster_centroids


def routing_agent(state):

    G = generate_grid_graph()
    G = block_roads_based_on_severity(G, state.flood_event["severity"], 42)

    centroids = compute_cluster_centroids(state.triaged_reports)

    routes = {}
    depot = (0, 0)

    for cid, (lat, lon) in centroids.items():
        target = latlon_to_grid(lat, lon)
        route = find_route(G, depot, target)
        routes[cid] = route

    state.routes = routes
    return state