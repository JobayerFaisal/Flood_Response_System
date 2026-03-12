# backend/tests/test_full_flow.py

from backend.core.event_bus import EventBus
from backend.core.incident_manager import IncidentManager
from backend.core.event_types import EventTypes
from backend.core.state_models import Volunteer

from backend.agents.triage_agent import TriageAgent
from backend.agents.command_agent import CommandAgent
from backend.agents.feedback_agent import FeedbackAgent

from backend.memory.performance_tracker import PerformanceTracker
from backend.memory.learning_engine import LearningEngine


# --------------------------------------------------
# 1️⃣ Setup Core Infrastructure
# --------------------------------------------------

event_bus = EventBus()
incident_manager = IncidentManager(event_bus)

state = incident_manager.get_state()


# --------------------------------------------------
# 2️⃣ Setup Learning Memory (Shared)
# --------------------------------------------------

performance_tracker = PerformanceTracker()
learning_engine = LearningEngine(performance_tracker)


# --------------------------------------------------
# 3️⃣ Seed Volunteers (STRICT MODEL OBJECTS)
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
# 4️⃣ Initialize Agents (Proper Injection)
# --------------------------------------------------

triage_agent = TriageAgent(event_bus, incident_manager)

command_agent = CommandAgent(
    event_bus,
    incident_manager,
    learning_engine
)

feedback_agent = FeedbackAgent(
    event_bus,
    incident_manager,
    performance_tracker
)

triage_agent.register()
command_agent.register()
feedback_agent.register()


# --------------------------------------------------
# 5️⃣ Debug Listener
# --------------------------------------------------

def on_mission_assigned(payload):
    print("\n✅ MISSION ASSIGNED EVENT RECEIVED")
    print(payload)

event_bus.subscribe(EventTypes.MISSION_ASSIGNED, on_mission_assigned)


# --------------------------------------------------
# 6️⃣ Trigger System with Critical Report
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
# 7️⃣ Simulate Volunteer Completion (Learning Test)
# --------------------------------------------------

# Get first mission
mission_ids = list(state.missions.keys())

if mission_ids:
    mission_id = mission_ids[0]

    event_bus.publish(
        EventTypes.VOLUNTEER_REPORT_RECEIVED,
        {
            "mission_id": mission_id,
            "status": "COMPLETED"
        }
    )


# --------------------------------------------------
# 8️⃣ Print Final System State
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

print("\n----- LEARNING MEMORY -----")
for vid in state.volunteers:
    success_rate = performance_tracker.get_success_rate(vid)
    print(f"{vid} | Success Rate: {success_rate:.2f}")