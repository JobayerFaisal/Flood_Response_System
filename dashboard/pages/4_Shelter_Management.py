import streamlit as st
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from dashboard.utils.state import init_state
from backend.planning.shelter_allocator import generate_shelters, allocate_to_shelters
from backend.planning.clustering import cluster_reports
from backend.planning.resource_allocation import estimate_cluster_demand

init_state()
st.title("🏠 Shelter Management")

if st.session_state.timeline is None:
    st.warning("Run simulation first.")
    st.stop()

step_data = st.session_state.timeline[-1]
clustered = cluster_reports(step_data["reports"])
demand = estimate_cluster_demand(clustered)

shelters = generate_shelters()
plan, overflow = allocate_to_shelters(demand, shelters)

st.json(plan)
if overflow > 0:
    st.error(f"Overflow: {overflow} people")