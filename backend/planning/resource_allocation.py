# backend/planning/resource_allocation.py

def estimate_cluster_demand(clustered_reports):
    """
    Estimate demand per cluster based on urgency.
    Higher urgency = higher weight.
    """
    demand = {}

    for r in clustered_reports:
        cid = r.get("cluster_id")
        if cid == -1:
            continue

        weight = 2 if r["urgency"] >= 4 else 1
        demand.setdefault(cid, 0)
        demand[cid] += weight

    return demand


def allocate_boats(cluster_demand, boat_count=3, boat_capacity=50):
    """
    Allocate limited boats to clusters.
    Returns allocation plan.
    """

    allocation = {}
    remaining_boats = boat_count

    # Sort clusters by demand descending
    sorted_clusters = sorted(
        cluster_demand.items(),
        key=lambda x: x[1],
        reverse=True
    )

    for cid, demand in sorted_clusters:
        if remaining_boats <= 0:
            allocation[cid] = {
                "boats_assigned": 0,
                "capacity_served": 0,
                "unmet_demand": demand
            }
            continue

        boats_needed = (demand // boat_capacity) + 1
        boats_assigned = min(boats_needed, remaining_boats)

        capacity_served = boats_assigned * boat_capacity
        unmet = max(0, demand - capacity_served)

        allocation[cid] = {
            "boats_assigned": boats_assigned,
            "capacity_served": capacity_served,
            "unmet_demand": unmet
        }

        remaining_boats -= boats_assigned

    return allocation