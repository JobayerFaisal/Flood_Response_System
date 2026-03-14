# tests/test_environmental_to_response_flow.py

from datetime import datetime

from backend.core.event_bus import EventBus
from backend.core.incident_manager import IncidentManager
from backend.core.event_types import EventTypes
from backend.core.state_models import Volunteer

from backend.environmental.agent.environmental_detection_agent import EnvironmentalDetectionAgent
from backend.agents.flood_response_coordinator import FloodResponseCoordinator
from backend.agents.command_agent import CommandAgent
from backend.agents.feedback_agent import FeedbackAgent

from backend.memory.persistent_store import PersistentStore
from backend.memory.global_learning_engine import GlobalLearningEngine


def main():
    event_bus = EventBus()
    incident_manager = IncidentManager(event_bus)
    state = incident_manager.get_state()

    # Shared learning infra
    store = PersistentStore()
    global_learning_engine = GlobalLearningEngine(store)

    # Seed volunteers
    state.volunteers = {
        "V1": Volunteer(
            volunteer_id="V1",
            location=(23.74, 90.38),
            skills=["rescue"],
            equipment=["boat"],
            available=True
        ),
        "V2": Volunteer(
            volunteer_id="V2",
            location=(23.80, 90.42),
            skills=["general"],
            equipment=[],
            available=True
        )
    }

    # Agents
    environmental_agent = EnvironmentalDetectionAgent(event_bus, incident_manager)
    coordinator = FloodResponseCoordinator(event_bus, incident_manager)
    command_agent = CommandAgent(event_bus, incident_manager, global_learning_engine)
    feedback_agent = FeedbackAgent(event_bus, incident_manager, global_learning_engine)

    environmental_agent.register()
    coordinator.register()
    command_agent.register()
    feedback_agent.register()

    def on_mission_assigned(payload):
        print("\n✅ MISSION ASSIGNED")
        print(payload)

    event_bus.subscribe(EventTypes.MISSION_ASSIGNED, on_mission_assigned)

    # Publish environmental signals
    event_bus.publish(
        EventTypes.WEATHER_UPDATE,
        {
            "station_id": "WS-001",
            "rainfall_mm": 135.0,
            "river_level_m": 8.2,
            "danger_level_m": 6.8,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )

    event_bus.publish(
        EventTypes.SATELLITE_UPDATE,
        {
            "polygon_geojson": {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [[
                                [90.35, 23.72],
                                [90.40, 23.72],
                                [90.40, 23.77],
                                [90.35, 23.77],
                                [90.35, 23.72]
                            ]]
                        },
                        "properties": {"zone": "Kaliganj"}
                    }
                ]
            },
            "confidence": 0.91,
            "water_extent_score": 0.82,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )

    event_bus.publish(
        EventTypes.SOCIAL_REPORT_RECEIVED,
        {
            "report_id": "R-1001",
            "text": "People stuck on roof and need rescue",
            "lat": 23.744,
            "lon": 90.386,
            "urgency": 5,
            "credibility": 0.93,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )

    print("\n----- FINAL INCIDENT STATE -----")
    print(f"Status: {state.status}")
    print(f"Severity: {state.severity}")
    print(f"Confidence: {state.confidence}")
    print(f"Missions: {len(state.missions)}")

    print("\n----- MISSIONS -----")
    for mission_id, mission in state.missions.items():
        print(
            f"{mission_id} | Type: {mission.type} | "
            f"Priority: {mission.priority} | Status: {mission.status} | "
            f"Assigned: {mission.assigned_volunteer}"
        )

    print("\n----- TIMELINE -----")
    for entry in state.timeline:
        print(entry)


if __name__ == "__main__":
    main()