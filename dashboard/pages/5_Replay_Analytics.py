# dashboard/pages/5_Replay_Analytics.py

import os
import sys
from collections import Counter

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

init_dashboard_state()

bridge = st.session_state["backend_bridge"]
update_from_incident_state(bridge.get_incident_state())
update_from_environmental_payload(bridge.get_latest_environmental_payload())

state = bridge.get_incident_state()
timeline = state.timeline or []
missions = state.missions or {}
volunteers = state.volunteers or {}

st.title("📈 Replay & Analytics — Sylhet Division")

selected_division = st.selectbox("Division", ["Sylhet"], index=0) or "Sylhet"
selected_district = st.selectbox(
    "District",
    ["All", "Sylhet", "Moulvibazar", "Habiganj", "Sunamganj"],
    index=0
) or "All"


def mission_matches(mission, district: str) -> bool:
    if district == "All":
        return True
    try:
        return bool(mission.report and mission.report.get("district") == district)
    except Exception:
        return False


def volunteer_matches(volunteer, district: str) -> bool:
    if district == "All":
        return volunteer.division == selected_division
    return volunteer.division == selected_division and volunteer.district == district


filtered_missions = {
    mission_id: mission
    for mission_id, mission in missions.items()
    if mission_matches(mission, selected_district)
}

filtered_volunteers = {
    volunteer_id: volunteer
    for volunteer_id, volunteer in volunteers.items()
    if volunteer_matches(volunteer, selected_district)
}

filtered_timeline = []
for entry in timeline:
    entry_district = entry.get("district")
    if selected_district == "All":
        filtered_timeline.append(entry)
    elif entry_district == selected_district or entry_district is None:
        filtered_timeline.append(entry)

mission_status_counts = Counter(m.status for m in filtered_missions.values())
completed = mission_status_counts.get("COMPLETED", 0)
failed = mission_status_counts.get("FAILED", 0)
total_missions = len(filtered_missions)
success_rate = (completed / total_missions) if total_missions else 0.0

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Timeline Events", len(filtered_timeline))
with col2:
    st.metric("Total Missions", total_missions)
with col3:
    st.metric("Mission Success Rate", f"{success_rate:.0%}")
with col4:
    st.metric("Current Severity", state.severity or 0)

st.markdown("---")
st.subheader("Replay Timeline")

if filtered_timeline:
    selected_idx = st.slider(
        "Select timeline step",
        min_value=0,
        max_value=len(filtered_timeline) - 1,
        value=len(filtered_timeline) - 1,
        step=1,
    )

    selected_event = filtered_timeline[selected_idx]

    col_a, col_b = st.columns([1, 1])

    with col_a:
        st.write("Selected Timeline Entry")
        st.json(selected_event)

    with col_b:
        st.write("Event Progress")
        replay_rows = []
        for i, entry in enumerate(filtered_timeline):
            replay_rows.append({
                "Step": i,
                "Event": entry.get("event"),
                "Severity": entry.get("severity"),
                "Detected": entry.get("detected"),
                "District": entry.get("district"),
                "Volunteer ID": entry.get("volunteer_id"),
                "Mission ID": entry.get("mission_id"),
                "Timestamp": entry.get("timestamp"),
            })
        replay_df = pd.DataFrame(replay_rows)
        st.dataframe(replay_df, use_container_width=True, height=320)
else:
    st.info("No timeline data available yet.")

st.markdown("---")
st.subheader("Mission Analytics")

if filtered_missions:
    mission_rows = []
    for mission_id, mission in filtered_missions.items():
        mission_rows.append({
            "Mission ID": mission_id,
            "District": mission.report.get("district") if mission.report else None,
            "Type": str(mission.type),
            "Priority": mission.priority,
            "Status": mission.status,
            "Assigned Volunteer": mission.assigned_volunteer,
            "Created At": str(mission.created_at),
        })

    mission_df = pd.DataFrame(mission_rows)
    st.dataframe(mission_df, use_container_width=True)

    status_counter = Counter(mission_df["Status"])
    status_df = pd.DataFrame({
        "Status": list(status_counter.keys()),
        "Count": list(status_counter.values())
    })
    st.bar_chart(status_df.set_index("Status"))
else:
    st.info("No mission data available.")

st.markdown("---")
st.subheader("Volunteer Analytics")

if filtered_volunteers:
    volunteer_rows = []
    for volunteer_id, volunteer in filtered_volunteers.items():
        assigned_count = 0
        completed_count = 0
        failed_count = 0

        for _, mission in filtered_missions.items():
            if mission.assigned_volunteer == volunteer_id:
                assigned_count += 1
                if mission.status == "COMPLETED":
                    completed_count += 1
                elif mission.status == "FAILED":
                    failed_count += 1

        volunteer_rows.append({
            "Volunteer ID": volunteer_id,
            "Division": volunteer.division,
            "District": volunteer.district,
            "Available": volunteer.available,
            "Skills": ", ".join(volunteer.skills),
            "Assigned Missions": assigned_count,
            "Completed Missions": completed_count,
            "Failed Missions": failed_count,
            "Location": str(volunteer.location),
        })

    volunteer_df = pd.DataFrame(volunteer_rows)
    st.dataframe(volunteer_df, use_container_width=True)
else:
    st.info("No volunteer data available.")

st.markdown("---")
st.subheader("Replay Map Snapshot")

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

polygon_geojson = state.flood_polygon
m = folium.Map(location=default_center, zoom_start=10)

if polygon_geojson:
    try:
        polygon_district = polygon_geojson["features"][0]["properties"].get("district")
    except Exception:
        polygon_district = None

    if selected_district == "All" or polygon_district == selected_district:
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
        radius=5,
        color=color,
        fill=True,
        fill_opacity=0.9,
        popup=f"{volunteer.volunteer_id} | {volunteer.district} | Available: {volunteer.available}",
    ).add_to(m)

st_folium(m, width=1100, height=550)

st.markdown("---")
st.subheader("Raw Event Log")

event_log = bridge.get_event_log()
if event_log:
    if st.checkbox("Show raw event log"):
        for event in event_log[-50:]:
            st.json(event)
else:
    st.info("No raw events recorded yet.")