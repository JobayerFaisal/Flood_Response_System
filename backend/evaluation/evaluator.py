# backendbackend/evaluation/evaluator.py

import numpy as np


def compute_unmet_ratio(cluster_demand, allocation_plan):
    total_demand = sum(cluster_demand.values())
    total_unmet = sum(v["unmet_demand"] for v in allocation_plan.values())

    if total_demand == 0:
        return 0.0

    return total_unmet / total_demand


def compute_resource_utilization(allocation_plan, boat_count, boat_capacity):
    total_capacity = boat_count * boat_capacity
    used_capacity = sum(v["capacity_served"] for v in allocation_plan.values())

    if total_capacity == 0:
        return 0.0

    return used_capacity / total_capacity


def compute_average_route_length(routes):
    lengths = [len(r) for r in routes.values() if r]

    if not lengths:
        return 0.0

    return float(np.mean(lengths))


def compute_route_success_rate(routes):
    total = len(routes)
    success = sum(1 for r in routes.values() if r)

    if total == 0:
        return 0.0

    return success / total


def compute_high_urgency_coverage(clustered_reports, allocation_plan):
    high_urgency_total = 0
    high_urgency_served = 0

    for r in clustered_reports:
        if r["urgency"] >= 4:
            high_urgency_total += 1
            cid = r["cluster_id"]
            if cid in allocation_plan and allocation_plan[cid]["capacity_served"] > 0:
                high_urgency_served += 1

    if high_urgency_total == 0:
        return 0.0

    return high_urgency_served / high_urgency_total


def compute_fairness_gini(allocation_plan, cluster_demand):
    service_ratios = []

    for cid, demand in cluster_demand.items():
        served = allocation_plan.get(cid, {}).get("capacity_served", 0)

        if demand > 0:
            service_ratios.append(served / demand)

    if len(service_ratios) <= 1:
        return 0.0

    arr = np.array(service_ratios)
    diff_sum = np.sum(np.abs(arr[:, None] - arr[None, :]))
    gini = diff_sum / (2 * len(arr) ** 2 * np.mean(arr))

    return float(gini)


def evaluate_all(
    clustered_reports,
    cluster_demand,
    allocation_plan,
    routes,
    boat_count,
    boat_capacity,
):
    return {
        "coverage": 1 - compute_unmet_ratio(cluster_demand, allocation_plan),
        "unmet_demand_ratio": compute_unmet_ratio(cluster_demand, allocation_plan),
        "resource_utilization": compute_resource_utilization(
            allocation_plan, boat_count, boat_capacity
        ),
        "avg_route_length": compute_average_route_length(routes),
        "route_success_rate": compute_route_success_rate(routes),
        "high_urgency_coverage": compute_high_urgency_coverage(
            clustered_reports, allocation_plan
        ),
        "fairness_gini": compute_fairness_gini(allocation_plan, cluster_demand),
    }