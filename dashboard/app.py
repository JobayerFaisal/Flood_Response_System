# dashboard/app.py

import streamlit as st
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dashboard.utils.state import (
    init_dashboard_state,
    update_from_incident_state,
    update_from_environmental_payload,
)

st.set_page_config(
    page_title="National Flood Management BRAIN",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_dashboard_state()

bridge = st.session_state["backend_bridge"]

st.title("🌊 National Flood Management BRAIN")
st.caption("Judge-ready prototype for Sylhet Division flood intelligence and response coordination.")

with st.sidebar:
    st.header("Demo Controls")

    if st.button("▶ Run Sylhet Division Demo", use_container_width=True):
        bridge.run_sylhet_judge_demo()
        update_from_incident_state(bridge.get_incident_state())
        update_from_environmental_payload(bridge.get_latest_environmental_payload())
        st.success("Sylhet demo executed successfully.")

    if st.button("⟳ Reset System", use_container_width=True):
        bridge.reset_system()
        update_from_incident_state(bridge.get_incident_state())
        update_from_environmental_payload(bridge.get_latest_environmental_payload())
        st.info("System reset complete.")

    if st.button("Run Environmental Only", use_container_width=True):
        bridge.run_demo_environmental_detection()
        update_from_incident_state(bridge.get_incident_state())
        update_from_environmental_payload(bridge.get_latest_environmental_payload())
        st.success("Environmental detection executed.")

    if st.button("Complete First Mission", use_container_width=True):
        changed = bridge.complete_first_mission()
        update_from_incident_state(bridge.get_incident_state())
        update_from_environmental_payload(bridge.get_latest_environmental_payload())

        if changed:
            st.success("First mission marked completed.")
        else:
            st.warning("No mission available.")

st.markdown(
    """
    ### Demo flow
    Use **Run Sylhet Division Demo** for a complete one-click scenario:
    1. Environmental flood detection  
    2. Incident activation  
    3. Mission creation  
    4. Volunteer assignment  
    5. Mission completion  

    Then inspect the pages from the sidebar:
    - National Command Center
    - Incident Map
    - Mission Operations
    - Volunteer Operations
    - Replay & Analytics
    - AI Reasoning
    - Live Operations
    """
)