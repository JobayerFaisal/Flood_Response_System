import streamlit as st
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from dashboard.utils.state import init_state
from backend.detection.fusion_engine import detect_flood
from backend.planning.clustering import cluster_reports
from backend.planning.resource_allocation import estimate_cluster_demand, allocate_boats
from backend.evaluation.response_metrics import compute_coverage

init_state()
st.title("📝 Situation Report")

if st.session_state.timeline is None:
    st.warning("Run simulation first.")
    st.stop()

step_data = st.session_state.timeline[-1]
event = detect_flood(step_data)
clustered = cluster_reports(step_data["reports"])
demand = estimate_cluster_demand(clustered)
allocation = allocate_boats(demand, 3, 50)
coverage = compute_coverage(allocation, demand)

sitrep = {
    "severity": event.severity,
    "confidence": event.confidence,
    "trend": event.trend,
    "coverage": coverage,
    "reports": len(clustered),
    "hazards": event.hazards
}

st.json(sitrep)