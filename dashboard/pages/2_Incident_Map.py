# dashboard/pages/2_Incident_Map.py

import os
import sys
import streamlit as st
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
payload = st.session_state["latest_environmental_payload"]

st.title("🗺 Incident Map — Sylhet Division")

selected_division = st.selectbox("Division", ["Sylhet"], index=0) or "Sylhet"
selected_district = st.selectbox(
    "District",
    ["All", "Sylhet", "Moulvibazar", "Habiganj", "Sunamganj"],
    index=0
) or "All"

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

polygon_geojson = st.session_state["latest_polygon"]


def polygon_matches_district(polygon_geojson_obj, district: str) -> bool:
    if district == "All":
        return True
    try:
        props = polygon_geojson_obj["features"][0]["properties"]
        return props.get("district") == district
    except Exception:
        return False


if polygon_geojson and polygon_matches_district(polygon_geojson, selected_district):
    folium.GeoJson(
        polygon_geojson,
        style_function=lambda _: {
            "fillColor": "blue",
            "color": "blue",
            "weight": 2,
            "fillOpacity": 0.35,
        },
        tooltip="Detected Flood Area"
    ).add_to(m)

# Volunteer overlay
for volunteer in state.volunteers.values():
    if selected_district != "All" and volunteer.district != selected_district:
        continue

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

# Mission overlay
for mission_id, mission in state.missions.items():
    if not mission.report:
        continue

    mission_district = mission.report.get("district", "Unknown")
    if selected_district != "All" and mission_district != selected_district:
        continue

    lat = mission.report.get("lat")
    lon = mission.report.get("lon")

    if lat is None or lon is None:
        continue

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

st_folium(m, width=1100, height=650)

st.markdown("---")
st.subheader("Detection Snapshot")

if payload:
    snapshot = dict(payload)
    if selected_district == "All" or (
        payload.get("polygon_geojson")
        and polygon_matches_district(payload.get("polygon_geojson"), selected_district)
    ):
        st.json(snapshot)
    else:
        st.info("No detection snapshot for the selected district.")
else:
    st.info("No environmental detection payload available yet.")