# backend/planning/random_allocation.py

import random


def random_allocate_boats(cluster_demand, boat_count, boat_capacity, seed):
    random.seed(seed)

    clusters = list(cluster_demand.keys())
    allocation = {}
    boats = boat_count

    while boats > 0 and clusters:
        cid = random.choice(clusters)

        allocation.setdefault(cid, {
            "boats_assigned": 0,
            "capacity_served": 0,
            "unmet_demand": cluster_demand[cid]
        })

        allocation[cid]["boats_assigned"] += 1
        allocation[cid]["capacity_served"] += boat_capacity
        allocation[cid]["unmet_demand"] = max(
            0,
            cluster_demand[cid] - allocation[cid]["capacity_served"]
        )

        boats -= 1

    # Ensure all clusters exist in dict
    for cid in cluster_demand:
        allocation.setdefault(cid, {
            "boats_assigned": 0,
            "capacity_served": 0,
            "unmet_demand": cluster_demand[cid]
        })

    return allocation