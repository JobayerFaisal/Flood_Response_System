# backend/planning/routing.py

import networkx as nx
import random


def generate_grid_graph(size=20):
    G = nx.grid_2d_graph(size, size)
    return G


def block_roads_based_on_severity(G, severity):
    if severity >= 4:
        edges = list(G.edges())
        to_remove = int(len(edges) * 0.2)
        for edge in random.sample(edges, to_remove):
            G.remove_edge(*edge)
    return G


def find_route(G, start, end):
    try:
        path = nx.shortest_path(G, start, end)
        return path
    except:
        return None