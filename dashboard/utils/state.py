# dashboard/utils/state.py

import streamlit as st
from dashboard.utils.backend_bridge import BackendBridge


def init_dashboard_state():
    defaults = {
        "active_incident_id": None,
        "incident_status": "IDLE",
        "latest_detection": None,
        "latest_environmental_payload": None,
        "mission_count": 0,
        "active_volunteer_count": 0,
        "detected_flood_count": 0,
        "latest_confidence": 0.0,
        "latest_severity": 0,
        "latest_polygon": None,
        "latest_risk_factors": [],
        "timeline_entries": [],
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    if "backend_bridge" not in st.session_state:
        st.session_state["backend_bridge"] = BackendBridge()


def update_from_incident_state(incident_state):
    st.session_state["active_incident_id"] = incident_state.incident_id
    st.session_state["incident_status"] = incident_state.status
    st.session_state["mission_count"] = len(incident_state.missions)
    st.session_state["active_volunteer_count"] = sum(
        1 for v in incident_state.volunteers.values() if v.available
    )
    st.session_state["latest_severity"] = incident_state.severity or 0
    st.session_state["latest_confidence"] = incident_state.confidence or 0.0
    st.session_state["latest_polygon"] = incident_state.flood_polygon
    st.session_state["timeline_entries"] = incident_state.timeline


def update_from_environmental_payload(payload: dict | None):
    if not payload:
        return

    st.session_state["latest_environmental_payload"] = payload
    st.session_state["latest_confidence"] = payload.get("confidence", 0.0)
    st.session_state["latest_severity"] = payload.get("severity", 0)
    st.session_state["latest_polygon"] = payload.get("polygon_geojson")
    st.session_state["latest_risk_factors"] = payload.get("risk_factors", [])

    if payload.get("detected"):
        st.session_state["detected_flood_count"] += 1