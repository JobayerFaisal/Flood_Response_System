import streamlit as st
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from dashboard.utils.state import init_state
from backend.planning.clustering import cluster_reports
from backend.planning.resource_allocation import estimate_cluster_demand, allocate_boats

init_state()
st.title("🚑 Resource Planning")

if st.session_state.timeline is None:
    st.warning("Run simulation first.")
    st.stop()

step_data = st.session_state.timeline[-1]
clustered = cluster_reports(step_data["reports"])
demand = estimate_cluster_demand(clustered)
allocation = allocate_boats(demand, 3, 50)

st.json(demand)
st.json(allocation)