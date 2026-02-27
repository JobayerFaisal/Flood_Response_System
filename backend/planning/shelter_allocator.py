import math


def generate_shelters():
    """
    Static shelter locations with capacity.
    """
    return {
        "Shelter_A": {"grid": (2, 8), "capacity": 200, "occupied": 0},
        "Shelter_B": {"grid": (8, 8), "capacity": 150, "occupied": 0},
        "Shelter_C": {"grid": (5, 1), "capacity": 100, "occupied": 0},
    }


def distance(a, b):
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


def allocate_to_shelters(cluster_demand, shelters):
    """
    Allocate rescued people to nearest available shelter.
    """
    allocation = {}
    overflow = 0

    for cid, demand in cluster_demand.items():

        remaining = demand
        allocation[cid] = []

        # Sort shelters by proximity
        sorted_shelters = sorted(
            shelters.items(),
            key=lambda s: distance((0, 0), s[1]["grid"])
        )

        for shelter_name, shelter in sorted_shelters:

            available = shelter["capacity"] - shelter["occupied"]

            if available <= 0:
                continue

            assigned = min(available, remaining)

            shelter["occupied"] += assigned
            remaining -= assigned

            allocation[cid].append({
                "shelter": shelter_name,
                "assigned": assigned
            })

            if remaining <= 0:
                break

        if remaining > 0:
            overflow += remaining

    return allocation, overflow