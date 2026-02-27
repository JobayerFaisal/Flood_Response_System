# dashboard/pages/1_Control_Room.py

import streamlit as st
import folium
import sys
import os
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from streamlit_folium import st_folium
from dashboard.utils.state import init_state, run_simulation

from backend.detection.fusion_engine import detect_flood
from backend.planning.clustering import cluster_reports
from backend.planning.resource_allocation import estimate_cluster_demand, allocate_boats
from backend.planning.routing import generate_grid_graph, block_roads_based_on_severity, find_route, latlon_to_grid
from backend.planning.cluster_utils import compute_cluster_centroids

from backend.evaluation.evaluator import evaluate_all
from backend.evaluation.ground_truth_evaluator import (
    compute_detection_iou,
    compute_high_urgency_precision,
    compute_high_urgency_recall
)

from backend.planning.fair_allocation import fair_allocate_boats
from backend.planning.random_allocation import random_allocate_boats

from backend.agents.graph import build_graph
from backend.agents.state import AgentState


# -------------------------------------------------
# Init
# -------------------------------------------------
init_state()
st.title("🛰 Control Room")

scenario = st.sidebar.selectbox("Scenario", ["S3"])
seed = st.sidebar.number_input("Seed", value=42)
steps = st.sidebar.slider("Steps", 1, 10, 5)

if st.sidebar.button("Run Simulation"):
    run_simulation(scenario, seed, steps)

if st.session_state.timeline is None:
    st.warning("Run simulation first.")
    st.stop()

timeline = st.session_state.timeline
step_data = timeline[-1]

# -------------------------------------------------
# Detection & Clustering
# -------------------------------------------------
event = detect_flood(step_data)
clustered_reports = cluster_reports(step_data["reports"])
cluster_demand = estimate_cluster_demand(clustered_reports)

# -------------------------------------------------
# Manual Routing (for evaluation comparison)
# -------------------------------------------------
G = generate_grid_graph()
G = block_roads_based_on_severity(G, event.severity, seed)

depots = {"Depot A": (0, 0), "Depot B": (5, 5), "Depot C": (8, 2)}
centroids = compute_cluster_centroids(clustered_reports)

routes = {}
for cid, (lat, lon) in centroids.items():
    target = latlon_to_grid(lat, lon)
    best_route = None
    shortest = float("inf")
    for depot in depots.values():
        route = find_route(G, depot, target)
        if route and len(route) < shortest:
            best_route = route
            shortest = len(route)
    routes[cid] = best_route

# -------------------------------------------------
# Allocation Strategies (Benchmarking)
# -------------------------------------------------
greedy_plan = allocate_boats(cluster_demand, 3, 50)

cluster_urgency = {
    cid: sum(r["urgency"] for r in clustered_reports if r["cluster_id"] == cid)
    for cid in cluster_demand
}
fair_plan = fair_allocate_boats(cluster_demand, cluster_urgency, 3, 50)
random_plan = random_allocate_boats(cluster_demand, 3, 50, seed)

# -------------------------------------------------
# Strategy Evaluation
# -------------------------------------------------
greedy_metrics = evaluate_all(clustered_reports, cluster_demand, greedy_plan, routes, 3, 50)
fair_metrics = evaluate_all(clustered_reports, cluster_demand, fair_plan, routes, 3, 50)
random_metrics = evaluate_all(clustered_reports, cluster_demand, random_plan, routes, 3, 50)

comparison_df = pd.DataFrame([
    {"Strategy": "Random", **random_metrics},
    {"Strategy": "Greedy", **greedy_metrics},
    {"Strategy": "Fairness-Aware", **fair_metrics},
])

# -------------------------------------------------
# Ground Truth Scoring
# -------------------------------------------------
ground_truth = step_data["ground_truth"]

iou = compute_detection_iou(
    event.affected_area_geojson,
    ground_truth["true_flood_polygon"]
)

precision = compute_high_urgency_precision(
    clustered_reports,
    greedy_plan,
    ground_truth["true_high_urgency_reports"]
)

recall = compute_high_urgency_recall(
    clustered_reports,
    greedy_plan,
    ground_truth["true_high_urgency_reports"]
)

# -------------------------------------------------
# Multi-Agent Orchestration
# -------------------------------------------------
graph = build_graph()

agent_state = AgentState(
    flood_event=event.dict(),
    reports=step_data["reports"],
)

trace_outputs = []

for step in graph.stream(agent_state):
    trace_outputs.append(step)

final_plan = trace_outputs[-1]["command"]["final_plan"]

# -------------------------------------------------
# Layout
# -------------------------------------------------
col1, col2 = st.columns([2, 1])

# ---------------- MAP ----------------
with col1:
    centroid_lat, centroid_lon = event.centroid
    m = folium.Map(location=[centroid_lat, centroid_lon], zoom_start=13)

    folium.GeoJson(event.affected_area_geojson).add_to(m)

    base_lat, base_lon = 23.0, 90.0

    for name, (r, c) in depots.items():
        folium.Marker(
            location=[base_lat + r * 0.01, base_lon + c * 0.01],
            popup=name
        ).add_to(m)

    for r in clustered_reports:
        folium.CircleMarker(
            location=[r["lat"], r["lon"]],
            radius=4,
            color="red"
        ).add_to(m)

    for route in routes.values():
        if route:
            coords = [(base_lat + r * 0.01, base_lon + c * 0.01) for r, c in route]
            folium.PolyLine(coords, color="orange").add_to(m)

    st_folium(m, width=900, height=600)

# ---------------- METRICS ----------------
with col2:

    st.subheader("Incident Overview")
    st.metric("Severity", event.severity)
    st.metric("Confidence", round(event.confidence, 2))
    st.metric("Flood IoU", round(iou, 3))

    st.markdown("---")

    st.subheader("Urgency Detection")
    st.metric("Precision", round(precision, 3))
    st.metric("Recall", round(recall, 3))

    st.markdown("---")

    st.subheader("Strategy Comparison")
    st.dataframe(comparison_df.set_index("Strategy"))

    st.markdown("---")

    st.markdown("---")
    st.subheader("🧠 Multi-Agent Final Plan")
    st.json(final_plan)

    if "knowledge_references" in final_plan:
        st.subheader("📚 Retrieved Knowledge")

        for k, v in final_plan["knowledge_references"].items():
            with st.expander(f"{k}"):
                st.write(v)

    st.markdown("---")
    st.subheader("🧠 Agent Reasoning Trace")

    for step in trace_outputs:
        for node_name, node_output in step.items():
            with st.expander(f"{node_name.upper()} Agent Output"):
                st.json(node_output)