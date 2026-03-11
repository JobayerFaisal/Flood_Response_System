from backend.core.event_bus import EventBus
from backend.core.incident_manager import IncidentManager
from backend.agents.triage_agent import TriageAgent
from backend.core.event_types import EventTypes

bus = EventBus()
manager = IncidentManager(bus)

triage = TriageAgent(bus, manager)
triage.register()

# simulate report
bus.publish(
    EventTypes.SOCIAL_REPORT_RECEIVED,
    {
        "report_id": "R1",
        "lat": 23.1,
        "lon": 90.2,
        "urgency": 5,
        "credibility": 0.9
    }
)

print(manager.get_state())