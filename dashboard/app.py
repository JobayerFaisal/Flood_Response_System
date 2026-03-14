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

with st.sidebar:
    st.header("Control Panel")

    if st.button("Run Environmental Demo"):
        bridge.run_demo_environmental_detection()
        update_from_incident_state(bridge.get_incident_state())
        update_from_environmental_payload(bridge.get_latest_environmental_payload())
        st.success("Environmental detection flow executed.")

    if st.button("Complete First Mission"):
        changed = bridge.complete_first_mission()
        update_from_incident_state(bridge.get_incident_state())
        update_from_environmental_payload(bridge.get_latest_environmental_payload())

        if changed:
            st.success("First mission marked completed.")
        else:
            st.warning("No mission available to complete.")

st.markdown(
    """
    Use the sidebar to trigger the demo workflow, then navigate through pages:
    - National Command Center
    - Incident Map
    """
)