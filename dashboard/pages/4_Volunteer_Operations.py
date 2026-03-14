# dashboard/pages/4_Volunteer_Operations.py

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

init_dashboard_state()

bridge = st.session_state["backend_bridge"]
update_from_incident_state(bridge.get_incident_state())
update_from_environmental_payload(bridge.get_latest_environmental_payload())

state = bridge.get_incident_state()

st.title("👥 Volunteer Operations — Sylhet Division")

selected_division = st.selectbox("Division", ["Sylhet"], index=0)
selected_district = st.selectbox(
    "District",
    ["All", "Sylhet", "Moulvibazar", "Habiganj", "Sunamganj"],
    index=0
)

volunteers = {
    volunteer_id: volunteer
    for volunteer_id, volunteer in state.volunteers.items()
    if volunteer.division == selected_division
    and (selected_district == "All" or volunteer.district == selected_district)
}

missions = state.missions

total_volunteers = len(volunteers)
available_volunteers = [v for v in volunteers.values() if v.available]
busy_volunteers = [v for v in volunteers.values() if not v.available]

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Volunteers", total_volunteers)
with col2:
    st.metric("Available", len(available_volunteers))
with col3:
    st.metric("Busy", len(busy_volunteers))

st.markdown("---")
st.subheader("Volunteer Registry")

if volunteers:
    rows = []
    for volunteer_id, volunteer in volunteers.items():
        assigned_mission = None

        for mission_id, mission in missions.items():
            if mission.assigned_volunteer == volunteer_id and mission.status in [
                "CREATED", "ASSIGNED", "EN_ROUTE", "ACTIVE"
            ]:
                assigned_mission = mission_id
                break

        rows.append({
            "Volunteer ID": volunteer.volunteer_id,
            "Division": volunteer.division,
            "District": volunteer.district,
            "Available": volunteer.available,
            "Skills": ", ".join(volunteer.skills),
            "Equipment": ", ".join(volunteer.equipment),
            "Location": str(volunteer.location),
            "Assigned Mission": assigned_mission,
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True)
else:
    st.info("No volunteers registered for the selected district.")

st.markdown("---")
st.subheader("Volunteer Details")

volunteer_ids = list(volunteers.keys())

if volunteer_ids:
    selected_volunteer_id = st.selectbox("Select Volunteer", volunteer_ids)
    volunteer = volunteers[selected_volunteer_id]

    assigned_missions = []
    for mission_id, mission in missions.items():
        if mission.assigned_volunteer == selected_volunteer_id:
            assigned_missions.append({
                "mission_id": mission_id,
                "status": mission.status,
                "priority": mission.priority,
                "type": str(mission.type),
                "district": mission.report.get("district") if mission.report else None,
            })

    col_a, col_b = st.columns([1, 1])

    with col_a:
        st.json({
            "volunteer_id": volunteer.volunteer_id,
            "division": volunteer.division,
            "district": volunteer.district,
            "available": volunteer.available,
            "skills": volunteer.skills,
            "equipment": volunteer.equipment,
            "location": volunteer.location,
        })

    with col_b:
        if assigned_missions:
            st.write("Assigned / Historical Missions")
            st.json(assigned_missions)
        else:
            st.info("No missions linked to this volunteer.")
else:
    st.info("No volunteer available for the selected district.")

st.markdown("---")
st.subheader("Volunteer Controls")

if volunteer_ids:
    col_x, col_y = st.columns(2)

    with col_x:
        if st.button("Set Available"):
            volunteers[selected_volunteer_id].available = True
            update_from_incident_state(bridge.get_incident_state())
            st.success(f"{selected_volunteer_id} set to available.")

    with col_y:
        if st.button("Set Unavailable"):
            volunteers[selected_volunteer_id].available = False
            update_from_incident_state(bridge.get_incident_state())
            st.warning(f"{selected_volunteer_id} set to unavailable.")

st.markdown("---")
st.subheader("Recent Volunteer / Mission Timeline")

timeline = state.timeline
relevant_events = [
    t for t in timeline
    if t.get("volunteer_id") is not None
    or "MISSION" in str(t.get("event", ""))
    or t.get("district") == selected_district
]

if relevant_events:
    for entry in reversed(relevant_events[-10:]):
        st.json(entry)
else:
    st.info("No volunteer-related events yet.")