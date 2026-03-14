# dashboard/pages/1_National_Command_Center.py

import os
import sys
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from dashboard.utils.state import (
    init_dashboard_state,
    update_from_incident_state,
    update_from_environmental_payload,
)

init_dashboard_state()

bridge = st.session_state["backend_bridge"]
update_from_incident_state(bridge.get_incident_state())
update_from_environmental_payload(bridge.get_latest_environmental_payload())

state = bridge.get_incident_state()
timeline = state.timeline or []
missions = state.missions or {}
volunteers = state.volunteers or {}
payload = bridge.get_latest_environmental_payload()

st.title("🛰 National Command Center — Sylhet Division")

selected_division = st.selectbox("Division", ["Sylhet"], index=0) or "Sylhet"
selected_district = st.selectbox(
    "District",
    ["All", "Sylhet", "Moulvibazar", "Habiganj", "Sunamganj"],
    index=0
) or "All"


def mission_matches_district(mission, district: str) -> bool:
    if district == "All":
        return True
    try:
        return bool(mission.report and mission.report.get("district") == district)
    except Exception:
        return False


def volunteer_matches_district(volunteer, district: str) -> bool:
    if district == "All":
        return volunteer.division == selected_division
    return volunteer.division == selected_division and volunteer.district == district


def timeline_matches_district(entry: dict, district: str) -> bool:
    if district == "All":
        return True
    entry_district = entry.get("district")
    return entry_district == district or entry_district is None


def payload_matches_district(current_payload: dict | None, district: str) -> bool:
    if not current_payload:
        return False
    if district == "All":
        return True
    try:
        polygon = current_payload.get("polygon_geojson")
        if not polygon:
            return True
        props = polygon["features"][0]["properties"]
        return props.get("district") == district
    except Exception:
        return False


filtered_missions = {
    mission_id: mission
    for mission_id, mission in missions.items()
    if mission_matches_district(mission, selected_district)
}

filtered_volunteers = {
    volunteer_id: volunteer
    for volunteer_id, volunteer in volunteers.items()
    if volunteer_matches_district(volunteer, selected_district)
}

filtered_timeline = [
    entry for entry in timeline
    if timeline_matches_district(entry, selected_district)
]

filtered_payload = payload if payload_matches_district(payload, selected_district) else None

detected_flood_events = sum(
    1
    for entry in filtered_timeline
    if entry.get("event") == "ENVIRONMENTAL_DETECTION_UPDATED" and entry.get("detected") is True
)

active_missions = sum(
    1
    for mission in filtered_missions.values()
    if mission.status in ["CREATED", "ASSIGNED", "EN_ROUTE", "ACTIVE"]
)

available_volunteers = sum(
    1
    for volunteer in filtered_volunteers.values()
    if volunteer.available
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Incident Status", state.status)

with col2:
    st.metric("Severity", state.severity or 0)

with col3:
    st.metric("Confidence", round(state.confidence or 0.0, 3))

with col4:
    st.metric("Detected Flood Events", detected_flood_events)

col5, col6, col7 = st.columns(3)

with col5:
    st.metric("Mission Count", len(filtered_missions))

with col6:
    st.metric("Active Missions", active_missions)

with col7:
    st.metric("Available Volunteers", available_volunteers)

st.markdown("---")

left, right = st.columns([1.2, 1])

with left:
    st.subheader("Operational Summary")

    st.write(f"**Division:** {selected_division}")
    st.write(f"**District:** {selected_district}")
    st.write(f"**Active Incident ID:** {state.incident_id}")
    st.write(f"**Current Status:** {state.status}")
    st.write(f"**Flood Polygon Available:** {state.flood_polygon is not None}")
    st.write(f"**Reports Stored:** {len(state.reports)}")

    st.markdown("### Mission Snapshot")
    if filtered_missions:
        for mission_id, mission in list(filtered_missions.items())[:5]:
            district = mission.report.get("district") if mission.report else "Unknown"
            st.info(
                f"{mission_id[:8]} | {mission.priority} | {mission.status} | "
                f"{district} | {mission.assigned_volunteer}"
            )
    else:
        st.info("No missions for the selected district.")

with right:
    st.subheader("Risk Factors")

    risk_factors = []
    if filtered_payload:
        risk_factors = filtered_payload.get("risk_factors", [])

    if risk_factors:
        for risk in risk_factors:
            st.warning(risk)
    else:
        st.info("No risk factors available for the selected district.")

    st.markdown("### Latest Detection Snapshot")
    if filtered_payload:
        st.json({
            "detected": filtered_payload.get("detected"),
            "severity": filtered_payload.get("severity"),
            "confidence": filtered_payload.get("confidence"),
            "evidence_refs": filtered_payload.get("evidence_refs", []),
        })
    else:
        st.info("No district-specific detection snapshot available.")

st.markdown("---")
st.subheader("Timeline")

if filtered_timeline:
    for entry in reversed(filtered_timeline[-10:]):
        st.json(entry)
else:
    st.info("No timeline events yet for the selected district.")