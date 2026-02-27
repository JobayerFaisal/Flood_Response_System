# backend/planning/routing.py

import networkx as nx
import random


def generate_grid_graph(size=20):
    return nx.grid_2d_graph(size, size)


def block_roads_based_on_severity(G, severity, seed):
    if severity >= 4:
        rng = random.Random(seed)  # deterministic per scenario

        edges = list(G.edges())
        remove_count = int(len(edges) * 0.2)

        for edge in rng.sample(edges, remove_count):
            if G.has_edge(*edge):
                G.remove_edge(*edge)

    return G

def find_route(G, start, end):
    try:
        return nx.shortest_path(G, start, end)
    except nx.NetworkXNoPath:
        return None


def latlon_to_grid(lat, lon):
    x = int((lat - 23.0) * 100)
    y = int((lon - 90.0) * 100)
    return (x, y)