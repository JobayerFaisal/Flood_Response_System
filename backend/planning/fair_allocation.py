def fair_allocate_boats(cluster_demand, cluster_urgency, boat_count, boat_capacity):
    """
    Allocate boats prioritizing urgency and balancing fairness.
    """

    boats = boat_count
    allocation = {}

    # Sort clusters by urgency descending
    sorted_clusters = sorted(
        cluster_demand.keys(),
        key=lambda cid: cluster_urgency.get(cid, 0),
        reverse=True
    )

    for cid in sorted_clusters:

        if boats <= 0:
            allocation[cid] = {
                "boats_assigned": 0,
                "capacity_served": 0,
                "unmet_demand": cluster_demand[cid]
            }
            continue

        boats_assigned = 1  # minimum fairness

        capacity_served = min(
            boat_capacity,
            cluster_demand[cid]
        )

        allocation[cid] = {
            "boats_assigned": boats_assigned,
            "capacity_served": capacity_served,
            "unmet_demand": cluster_demand[cid] - capacity_served
        }

        boats -= boats_assigned

    return allocation