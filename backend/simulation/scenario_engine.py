# backend/simulation/scenario_engine.py

from typing import Dict, Any

from backend.synthetic.scenario_runner import run_scenario
from backend.detection.fusion_engine import detect_flood
from backend.planning.clustering import cluster_reports
from backend.planning.resource_allocation import (
    estimate_cluster_demand,
    allocate_boats,
)
from backend.planning.routing import (
    generate_grid_graph,
    block_roads_based_on_severity,
    find_route,
    latlon_to_grid,
)
from backend.evaluation.response_metrics import (
    compute_coverage,
    compute_high_urgency_coverage,
    compute_unmet_demand_ratio,
    compute_resource_utilization,
    compute_route_success_rate,
    compute_average_route_length,
    estimate_response_time,
)
from backend.simulation.timeline_manager import TimelineManager


class ScenarioEngine:

    def __init__(self):
        self.timeline = TimelineManager()

    def execute_scenario(self, scenario_name: str, seed: int, steps: int) -> Dict[str, Any]:

        synthetic_timeline = run_scenario(
            name=scenario_name,
            seed=seed,
            steps=steps
        )

        for step_data in synthetic_timeline:

            # 1️⃣ Detection
            flood_event = detect_flood(step_data)

            # 2️⃣ Clustering
            clustered_reports = cluster_reports(step_data["reports"])

            # 3️⃣ Demand estimation
            cluster_demand = estimate_cluster_demand(clustered_reports)

            # 4️⃣ Allocation
            allocation_plan = allocate_boats(cluster_demand)

            # 5️⃣ Routing
            graph = generate_grid_graph(size=20)

            graph = block_roads_based_on_severity(
                graph,
                flood_event.severity,
                seed
            )
            routes = {}
            DEPOT = (10, 10)

            for cid in cluster_demand.keys():

                cluster_points = [
                    r for r in clustered_reports
                    if r.get("cluster_id") == cid
                ]

                if not cluster_points:
                    routes[cid] = None
                    continue

                avg_lat = sum(r["lat"] for r in cluster_points) / len(cluster_points)
                avg_lon = sum(r["lon"] for r in cluster_points) / len(cluster_points)

                target_node = latlon_to_grid(avg_lat, avg_lon)

                route = find_route(graph, DEPOT, target_node)

                routes[cid] = route

            # 6️⃣ Metrics
            coverage = compute_coverage(allocation_plan, cluster_demand)
            high_urgency = compute_high_urgency_coverage(clustered_reports, allocation_plan)
            unmet_ratio = compute_unmet_demand_ratio(allocation_plan, cluster_demand)
            utilization = compute_resource_utilization(allocation_plan, 3, 50)
            route_success = compute_route_success_rate(routes)
            avg_route_length = compute_average_route_length(routes)
            avg_response_time = estimate_response_time(routes)

            metrics = {
                "coverage": coverage,
                "high_urgency_coverage": high_urgency,
                "unmet_demand_ratio": unmet_ratio,
                "resource_utilization": utilization,
                "route_success_rate": route_success,
                "route_length": avg_route_length,
                "response_time": avg_response_time,
            }

            # Save step snapshot
            self.timeline.add_step(step_data["step"], {
                "timestamp": step_data["timestamp"],
                "flood_event": flood_event.dict(),
                "cluster_demand": cluster_demand,
                "allocation": allocation_plan,
                "routes": routes,
                "metrics": metrics
            })

        final_metrics = self.timeline.aggregate_metrics()

        return {
            "scenario": scenario_name,
            "seed": seed,
            "steps": steps,
            "timeline": self.timeline.get_all_steps(),
            "final_metrics": final_metrics
        }