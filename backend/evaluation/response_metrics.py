# backend/evaluation/response_metrics.py


def compute_coverage(allocation_plan, cluster_demand):
    """
    Overall demand coverage ratio.
    """
    total_demand = sum(cluster_demand.values())
    served = 0

    for cid, alloc in allocation_plan.items():
        served += min(
            cluster_demand.get(cid, 0),
            alloc.get("capacity_served", 0)
        )

    if total_demand == 0:
        return 1.0

    return served / total_demand


def compute_high_urgency_coverage(clustered_reports, allocation_plan):
    """
    % of high urgency reports (urgency >= 4)
    that belong to clusters that received boats.
    """
    high_urgency_total = 0
    high_urgency_served = 0

    for r in clustered_reports:
        if r.get("urgency", 0) >= 4:
            high_urgency_total += 1
            cid = r.get("cluster_id")
            if cid in allocation_plan and allocation_plan[cid]["boats_assigned"] > 0:
                high_urgency_served += 1

    if high_urgency_total == 0:
        return 1.0

    return high_urgency_served / high_urgency_total


def compute_unmet_demand_ratio(allocation_plan, cluster_demand):
    """
    How much demand remains unmet.
    """
    total_demand = sum(cluster_demand.values())
    total_unmet = sum(
        alloc.get("unmet_demand", 0)
        for alloc in allocation_plan.values()
    )

    if total_demand == 0:
        return 0.0

    return total_unmet / total_demand


def compute_resource_utilization(allocation_plan, boat_count, boat_capacity):
    """
    % of available rescue capacity used.
    """
    total_capacity = boat_count * boat_capacity
    used_capacity = sum(
        alloc.get("capacity_served", 0)
        for alloc in allocation_plan.values()
    )

    if total_capacity == 0:
        return 0.0

    return used_capacity / total_capacity


def compute_route_success_rate(routes):
    """
    % of clusters that have a valid route.
    """
    if not routes:
        return 1.0

    total = len(routes)
    successful = sum(1 for r in routes.values() if r is not None)

    return successful / total


def compute_average_route_length(routes):
    """
    Average path length for successful routes.
    """
    lengths = [
        len(route)
        for route in routes.values()
        if route is not None
    ]

    if not lengths:
        return 0.0

    return sum(lengths) / len(lengths)


def estimate_response_time(routes, speed_cells_per_minute=2):
    """
    Rough response time estimate based on grid distance.
    speed_cells_per_minute: synthetic movement speed
    """
    times = []

    for route in routes.values():
        if route is None:
            continue

        travel_time = len(route) / speed_cells_per_minute
        times.append(travel_time)

    if not times:
        return 0.0

    return sum(times) / len(times)