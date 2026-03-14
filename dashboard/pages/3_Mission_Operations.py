# dashboard/pages/3_Mission_Operations.py

import os
import sys
import streamlit as st
import pandas as pd

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

st.title("🚑 Mission Operations — Sylhet Division")

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
# Top summary
# -------------------------------------------------
active_missions = [
    m for m in filtered_missions.values()
    if m.status in ["CREATED", "ASSIGNED", "EN_ROUTE", "ACTIVE"]
]
completed_missions = [m for m in filtered_missions.values() if m.status == "COMPLETED"]
failed_missions = [m for m in filtered_missions.values() if m.status == "FAILED"]
available_volunteers = [v for v in filtered_volunteers.values() if v.available]

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Missions", len(filtered_missions))
with col2:
    st.metric("Active Missions", len(active_missions))
with col3:
    st.metric("Completed Missions", len(completed_missions))
with col4:
    st.metric("Available Volunteers", len(available_volunteers))

st.markdown("---")

# -------------------------------------------------
# Mission table
# -------------------------------------------------
st.subheader("Mission Queue")

if filtered_missions:
    rows = []
    for mission_id, mission in filtered_missions.items():
        rows.append({
            "Mission ID": mission_id,
            "Division": mission.report.get("division") if mission.report else None,
            "District": mission.report.get("district") if mission.report else None,
            "Type": str(mission.type),
            "Priority": mission.priority,
            "Status": mission.status,
            "Assigned Volunteer": mission.assigned_volunteer,
            "Cluster ID": mission.cluster_id,
            "Created At": str(mission.created_at),
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True)
else:
    st.info("No missions created yet for the selected district.")

st.markdown("---")

# -------------------------------------------------
# Mission action controls
# -------------------------------------------------
st.subheader("Mission Actions")

mission_ids = list(filtered_missions.keys())

if mission_ids:
    selected_mission_id = st.selectbox("Select Mission", mission_ids) or mission_ids[0]
    selected_mission = filtered_missions[selected_mission_id]

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        if st.button("Mark Completed"):
            bridge.event_bus.publish(
                EventTypes.VOLUNTEER_REPORT_RECEIVED,
                {
                    "mission_id": selected_mission_id,
                    "status": "COMPLETED",
                }
            )
            update_from_incident_state(bridge.get_incident_state())
            update_from_environmental_payload(bridge.get_latest_environmental_payload())
            st.success(f"Mission {selected_mission_id} marked COMPLETED.")

    with col_b:
        if st.button("Mark Failed"):
            bridge.event_bus.publish(
                EventTypes.VOLUNTEER_REPORT_RECEIVED,
                {
                    "mission_id": selected_mission_id,
                    "status": "FAILED",
                    "reason": "Operator-marked failure"
                }
            )
            update_from_incident_state(bridge.get_incident_state())
            update_from_environmental_payload(bridge.get_latest_environmental_payload())
            st.warning(f"Mission {selected_mission_id} marked FAILED.")

    with col_c:
        if st.button("Mark Active"):
            bridge.event_bus.publish(
                EventTypes.VOLUNTEER_REPORT_RECEIVED,
                {
                    "mission_id": selected_mission_id,
                    "status": "ACTIVE",
                }
            )
            update_from_incident_state(bridge.get_incident_state())
            update_from_environmental_payload(bridge.get_latest_environmental_payload())
            st.info(f"Mission {selected_mission_id} marked ACTIVE.")
else:
    st.info("No mission available for action in the selected district.")

st.markdown("---")

# -------------------------------------------------
# Mission details
# -------------------------------------------------
st.subheader("Selected Mission Details")

if mission_ids:
    st.json({
        "mission_id": selected_mission_id,
        "type": str(selected_mission.type),
        "priority": selected_mission.priority,
        "status": selected_mission.status,
        "assigned_volunteer": selected_mission.assigned_volunteer,
        "cluster_id": selected_mission.cluster_id,
        "report": selected_mission.report,
        "created_at": str(selected_mission.created_at),
    })

st.markdown("---")

# -------------------------------------------------
# Volunteer availability for this district
# -------------------------------------------------
st.subheader("District Volunteer Availability")

if filtered_volunteers:
    volunteer_rows = []
    for volunteer_id, volunteer in filtered_volunteers.items():
        volunteer_rows.append({
            "Volunteer ID": volunteer_id,
            "Division": volunteer.division,
            "District": volunteer.district,
            "Available": volunteer.available,
            "Skills": ", ".join(volunteer.skills),
            "Equipment": ", ".join(volunteer.equipment),
            "Location": str(volunteer.location),
        })

    volunteer_df = pd.DataFrame(volunteer_rows)
    st.dataframe(volunteer_df, use_container_width=True)
else:
    st.info("No volunteers available in the selected district.")

st.markdown("---")

# -------------------------------------------------
# Timeline slice
# -------------------------------------------------
st.subheader("Recent Mission Timeline")

timeline = state.timeline
mission_events = []
for t in timeline:
    if "MISSION" in str(t.get("event", "")) or t.get("mission_id") is not None:
        event_district = t.get("district")
        if selected_district == "All" or event_district in [selected_district, None]:
            mission_events.append(t)

if mission_events:
    for entry in reversed(mission_events[-10:]):
        st.json(entry)
else:
    st.info("No mission lifecycle events yet for the selected district.")