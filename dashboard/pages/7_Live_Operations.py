# dashboard/pages/7_Live_Operations.py

import os
import sys
import time
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from dashboard.utils.state import (
    init_dashboard_state,
    update_from_incident_state,
    update_from_environmental_payload,
)
from backend.core.event_types import EventTypes

init_dashboard_state()

bridge = st.session_state["backend_bridge"]
update_from_incident_state(bridge.get_incident_state())
update_from_environmental_payload(bridge.get_latest_environmental_payload())

state = bridge.get_incident_state()
missions = state.missions
volunteers = state.volunteers
payload = bridge.get_latest_environmental_payload()

st.title("📡 Live Operations — Sylhet Division")

with st.sidebar:
    st.header("Live Controls")
    auto_refresh = st.checkbox("Auto Refresh", value=False)
    refresh_seconds = st.slider("Refresh every (seconds)", 2, 30, 5)

    if st.button("Run Environmental Demo"):
        bridge.run_demo_environmental_detection()
        update_from_incident_state(bridge.get_incident_state())
        update_from_environmental_payload(bridge.get_latest_environmental_payload())
        st.success("Environmental flow executed.")

    if st.button("Complete First Mission"):
        changed = bridge.complete_first_mission()
        update_from_incident_state(bridge.get_incident_state())
        update_from_environmental_payload(bridge.get_latest_environmental_payload())
        if changed:
            st.success("First mission completed.")
        else:
            st.warning("No mission available.")

    if st.button("Refresh State"):
        update_from_incident_state(bridge.get_incident_state())
        update_from_environmental_payload(bridge.get_latest_environmental_payload())
        st.info("State refreshed.")

# -------------------------------------------------
# Division / district filters
# -------------------------------------------------
selected_division = st.selectbox("Division", ["Sylhet"], index=0) or "Sylhet"
selected_district = st.selectbox(
    "District",
    ["All", "Sylhet", "Moulvibazar", "Habiganj", "Sunamganj"],
    index=0
) or "All"

# -------------------------------------------------
# Filtering helpers
# -------------------------------------------------
def mission_matches_district(mission, district: str) -> bool:
    if district == "All":
        return True
    try:
        if mission.report:
            return mission.report.get("district") == district
    except Exception:
        return False
    return False


def volunteer_matches_district(volunteer, district: str) -> bool:
    if district == "All":
        return volunteer.division == selected_division
    return volunteer.division == selected_division and volunteer.district == district


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

# -------------------------------------------------
# Top bar
# -------------------------------------------------
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.metric("Incident Status", state.status)
with c2:
    st.metric("Severity", state.severity or 0)
with c3:
    st.metric("Confidence", round(state.confidence or 0.0, 3))
with c4:
    active_missions = sum(
        1 for m in filtered_missions.values()
        if m.status in ["CREATED", "ASSIGNED", "EN_ROUTE", "ACTIVE"]
    )
    st.metric("Active Missions", active_missions)
with c5:
    active_volunteers = sum(1 for v in filtered_volunteers.values() if not v.available)
    st.metric("Deployed Volunteers", active_volunteers)

st.markdown("---")

left, right = st.columns([1.7, 1])

# -------------------------------------------------
# Operational map
# -------------------------------------------------
with left:
    st.subheader("Operational Map")

    district_centers = {
        "Sylhet": [24.8949, 91.8687],
        "Moulvibazar": [24.4829, 91.7774],
        "Habiganj": [24.3745, 91.4155],
        "Sunamganj": [25.0658, 91.3950],
    }

    district_key: str = selected_district if selected_district != "All" else "Sylhet"

    default_center = district_centers.get(
        district_key,
        [24.8949, 91.8687]
    )

    m = folium.Map(location=default_center, zoom_start=10)

    polygon_geojson = state.flood_polygon
    if polygon_geojson:
        folium.GeoJson(
            polygon_geojson,
            style_function=lambda _: {
                "fillColor": "blue",
                "color": "blue",
                "weight": 2,
                "fillOpacity": 0.35,
            },
            tooltip="Flood Polygon"
        ).add_to(m)

    for volunteer in filtered_volunteers.values():
        lat, lon = volunteer.location
        color = "green" if volunteer.available else "red"
        folium.CircleMarker(
            location=[lat, lon],
            radius=6,
            color=color,
            fill=True,
            fill_opacity=0.9,
            popup=f"{volunteer.volunteer_id} | {volunteer.district} | Available: {volunteer.available}",
        ).add_to(m)

    for mission_id, mission in filtered_missions.items():
        if mission.report and mission.report.get("lat") is not None and mission.report.get("lon") is not None:
            lat = mission.report["lat"]
            lon = mission.report["lon"]

            if mission.status == "COMPLETED":
                color = "blue"
            elif mission.status == "FAILED":
                color = "black"
            elif mission.status in ["ASSIGNED", "EN_ROUTE", "ACTIVE"]:
                color = "orange"
            else:
                color = "purple"

            folium.Marker(
                location=[lat, lon],
                popup=f"{mission_id} | {mission.status} | {mission.priority}",
                icon=folium.Icon(color=color, icon="info-sign"),
            ).add_to(m)

    st_folium(m, width=900, height=620)

# -------------------------------------------------
# Side panel
# -------------------------------------------------
with right:
    st.subheader("Live Incident Feed")

    if payload:
        st.json({
            "division": selected_division,
            "district": selected_district,
            "detected": payload.get("detected"),
            "severity": payload.get("severity"),
            "confidence": payload.get("confidence"),
            "risk_factors": payload.get("risk_factors", []),
        })
    else:
        st.info("No live payload yet.")

    st.markdown("---")
    st.subheader("Mission Queue")

    if filtered_missions:
        rows = []
        for mission_id, mission in filtered_missions.items():
            rows.append({
                "Mission ID": mission_id[:8],
                "District": mission.report.get("district") if mission.report else None,
                "Type": str(mission.type),
                "Priority": mission.priority,
                "Status": mission.status,
                "Volunteer": mission.assigned_volunteer,
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, height=260)
    else:
        st.info("No missions yet.")

    st.markdown("---")
    st.subheader("Volunteer Status")

    if filtered_volunteers:
        rows = []
        for volunteer_id, volunteer in filtered_volunteers.items():
            rows.append({
                "Volunteer": volunteer_id,
                "District": volunteer.district,
                "Available": volunteer.available,
                "Skills": ", ".join(volunteer.skills),
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, height=220)
    else:
        st.info("No volunteers loaded.")

st.markdown("---")

# -------------------------------------------------
# Mission action console
# -------------------------------------------------
st.subheader("Mission Action Console")

mission_ids = list(filtered_missions.keys())
if mission_ids:
    selected_mission_id = st.selectbox(
        "Select Mission",
        mission_ids,
        key="live_ops_mission_select"
    ) or mission_ids[0]

    selected_mission = filtered_missions[selected_mission_id]

    ca, cb, cc = st.columns(3)

    with ca:
        if st.button("Set ACTIVE", key="live_set_active"):
            bridge.event_bus.publish(
                EventTypes.VOLUNTEER_REPORT_RECEIVED,
                {
                    "mission_id": selected_mission_id,
                    "status": "ACTIVE",
                }
            )
            update_from_incident_state(bridge.get_incident_state())
            st.info(f"{selected_mission_id} set ACTIVE.")

    with cb:
        if st.button("Set COMPLETED", key="live_set_completed"):
            bridge.event_bus.publish(
                EventTypes.VOLUNTEER_REPORT_RECEIVED,
                {
                    "mission_id": selected_mission_id,
                    "status": "COMPLETED",
                }
            )
            update_from_incident_state(bridge.get_incident_state())
            st.success(f"{selected_mission_id} completed.")

    with cc:
        if st.button("Set FAILED", key="live_set_failed"):
            bridge.event_bus.publish(
                EventTypes.VOLUNTEER_REPORT_RECEIVED,
                {
                    "mission_id": selected_mission_id,
                    "status": "FAILED",
                    "reason": "Live operator failure simulation"
                }
            )
            update_from_incident_state(bridge.get_incident_state())
            st.warning(f"{selected_mission_id} failed.")

    st.json({
        "mission_id": selected_mission_id,
        "type": str(selected_mission.type),
        "priority": selected_mission.priority,
        "status": selected_mission.status,
        "assigned_volunteer": selected_mission.assigned_volunteer,
        "report": selected_mission.report,
    })
else:
    st.info("No mission available for live operations.")

st.markdown("---")

# -------------------------------------------------
# Live event stream
# -------------------------------------------------
st.subheader("Recent Live Event Stream")

event_log = bridge.get_event_log()
if event_log:
    recent_events = event_log[-15:]
    for event in reversed(recent_events):
        st.json(event)
else:
    st.info("No events yet.")

if auto_refresh:
    time.sleep(refresh_seconds)
    st.rerun()