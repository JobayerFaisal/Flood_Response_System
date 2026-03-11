# backend/tests/test_full_flow.py

from backend.core.event_bus import EventBus
from backend.core.incident_manager import IncidentManager
from backend.core.event_types import EventTypes
from backend.core.state_models import Volunteer

from backend.agents.triage_agent import TriageAgent
from backend.agents.command_agent import CommandAgent


# --------------------------------------------------
# 1️⃣ Setup Core Infrastructure
# --------------------------------------------------

event_bus = EventBus()
incident_manager = IncidentManager(event_bus)

# Initialize empty incident state
state = incident_manager.get_state()


# --------------------------------------------------
# 2️⃣ Seed Volunteers (STRICT MODEL OBJECTS)
# --------------------------------------------------

state.volunteers = {
    "V1": Volunteer(
        volunteer_id="V1",
        location=(23.05, 90.10),
        skills=["rescue"],
        equipment=["boat"],
        available=True
    ),
    "V2": Volunteer(
        volunteer_id="V2",
        location=(23.20, 90.30),
        skills=["medical"],
        equipment=[],
        available=True
    )
}


# --------------------------------------------------
# 3️⃣ Initialize Agents
# --------------------------------------------------

triage_agent = TriageAgent(event_bus, incident_manager)
command_agent = CommandAgent(event_bus, incident_manager)

triage_agent.register()
command_agent.register()


# --------------------------------------------------
# 4️⃣ Listen to Mission Assigned Event (Debug)
# --------------------------------------------------

def on_mission_assigned(payload):
    print("\n✅ MISSION ASSIGNED EVENT RECEIVED")
    print(payload)

event_bus.subscribe(EventTypes.MISSION_ASSIGNED, on_mission_assigned)


# --------------------------------------------------
# 5️⃣ Trigger System with Critical Report
# --------------------------------------------------

event_bus.publish(
    EventTypes.SOCIAL_REPORT_RECEIVED,
    {
        "report_id": "R1",
        "lat": 23.06,
        "lon": 90.11,
        "urgency": 5,
        "credibility": 0.9
    }
)


# --------------------------------------------------
# 6️⃣ Print Final System State
# --------------------------------------------------

print("\n----- FINAL MISSIONS -----")
for mission_id, mission in state.missions.items():
    print(
        f"Mission ID: {mission_id} | "
        f"Type: {mission.type} | "
        f"Priority: {mission.priority} | "
        f"Status: {mission.status} | "
        f"Assigned: {mission.assigned_volunteer}"
    )

print("\n----- VOLUNTEER STATUS -----")
for vid, volunteer in state.volunteers.items():
    print(
        f"{vid} | Available: {volunteer.available} | "
        f"Location: {volunteer.location}"
    )