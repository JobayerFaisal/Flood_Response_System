# dashboard/utils/backend_bridge.py

import os
import sys
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.core.event_bus import EventBus
from backend.core.incident_manager import IncidentManager
from backend.core.event_types import EventTypes
from backend.core.state_models import Volunteer

from backend.environmental.agent.environmental_detection_agent import (
    EnvironmentalDetectionAgent,
)
from backend.agents.flood_response_coordinator import FloodResponseCoordinator
from backend.agents.command_agent import CommandAgent
from backend.agents.feedback_agent import FeedbackAgent

from backend.memory.persistent_store import PersistentStore
from backend.memory.global_learning_engine import GlobalLearningEngine


class BackendBridge:
    def __init__(self):
        self.event_bus = EventBus()
        self.incident_manager = IncidentManager(self.event_bus)

        self.store = PersistentStore()
        self.global_learning_engine = GlobalLearningEngine(self.store)

        self._seed_volunteers()
        self._register_agents()

        self.latest_environmental_payload = None

        self.event_bus.subscribe(
            EventTypes.FLOOD_INTELLIGENCE_UPDATED,
            self._capture_environmental_update
        )

    def _seed_volunteers(self):
        state = self.incident_manager.get_state()

        state.volunteers = {
            "V1": Volunteer(
                volunteer_id="V1",
                location=(24.8949, 91.8687),
                skills=["rescue"],
                equipment=["boat"],
                available=True,
                division="Sylhet",
                district="Sylhet",
            ),
            "V2": Volunteer(
                volunteer_id="V2",
                location=(24.4829, 91.7774),
                skills=["general"],
                equipment=[],
                available=True,
                division="Sylhet",
                district="Moulvibazar",
            ),
            "V3": Volunteer(
                volunteer_id="V3",
                location=(25.0658, 91.3950),
                skills=["rescue"],
                equipment=["boat"],
                available=True,
                division="Sylhet",
                district="Sunamganj",
            ),
            "V4": Volunteer(
                volunteer_id="V4",
                location=(24.3745, 91.4155),
                skills=["medical"],
                equipment=[],
                available=True,
                division="Sylhet",
                district="Habiganj",
            ),
        }

    def _register_agents(self):
        self.environmental_agent = EnvironmentalDetectionAgent(
            self.event_bus,
            self.incident_manager
        )
        self.coordinator = FloodResponseCoordinator(
            self.event_bus,
            self.incident_manager
        )
        self.command_agent = CommandAgent(
            self.event_bus,
            self.incident_manager,
            self.global_learning_engine
        )
        self.feedback_agent = FeedbackAgent(
            self.event_bus,
            self.incident_manager,
            self.global_learning_engine
        )

        self.environmental_agent.register()
        self.coordinator.register()
        self.command_agent.register()
        self.feedback_agent.register()

    def _capture_environmental_update(self, payload: dict):
        self.latest_environmental_payload = payload

    def get_incident_state(self):
        return self.incident_manager.get_state()

    def get_latest_environmental_payload(self):
        return self.latest_environmental_payload

    def get_event_log(self):
        return self.event_bus.get_event_log()

    def run_demo_environmental_detection(self):
        now = datetime.utcnow().isoformat()

        self.event_bus.publish(
            EventTypes.WEATHER_UPDATE,
            {
                "station_id": "SYL-WS-001",
                "rainfall_mm": 135.0,
                "river_level_m": 8.2,
                "danger_level_m": 6.8,
                "timestamp": now,
            }
        )

        self.event_bus.publish(
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
                                    [91.82, 24.84],
                                    [91.92, 24.84],
                                    [91.92, 24.94],
                                    [91.82, 24.94],
                                    [91.82, 24.84]
                                ]]
                            },
                            "properties": {
                                "division": "Sylhet",
                                "district": "Sylhet"
                            }
                        }
                    ]
                },
                "confidence": 0.91,
                "water_extent_score": 0.82,
                "timestamp": now,
            }
        )

        reports = [
            {
                "report_id": "SYL-R-1001",
                "text": "Water entered our house near Sylhet city fringe",
                "lat": 24.889,
                "lon": 91.881,
                "urgency": 4,
                "credibility": 0.88,
                "division": "Sylhet",
                "district": "Sylhet",
                "timestamp": now,
            },
            {
                "report_id": "SYL-R-1002",
                "text": "People stuck on the roof, need rescue boat",
                "lat": 24.892,
                "lon": 91.886,
                "urgency": 5,
                "credibility": 0.93,
                "division": "Sylhet",
                "district": "Sylhet",
                "timestamp": now,
            },
            {
                "report_id": "SYL-R-1003",
                "text": "Need medicine and dry food",
                "lat": 24.887,
                "lon": 91.879,
                "urgency": 3,
                "credibility": 0.81,
                "division": "Sylhet",
                "district": "Sylhet",
                "timestamp": now,
            },
        ]

        for report in reports:
            self.event_bus.publish(EventTypes.SOCIAL_REPORT_RECEIVED, report)

    def complete_first_mission(self):
        state = self.incident_manager.get_state()
        mission_ids = list(state.missions.keys())

        if not mission_ids:
            return False

        mission_id = mission_ids[0]

        self.event_bus.publish(
            EventTypes.VOLUNTEER_REPORT_RECEIVED,
            {
                "mission_id": mission_id,
                "status": "COMPLETED"
            }
        )
        return True