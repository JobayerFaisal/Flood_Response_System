# backend/core/incident_manager.py

import uuid
from datetime import datetime
from backend.core.state_models import IncidentState
from backend.core.event_bus import EventBus
from typing import Optional

class IncidentManager:

    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.state = IncidentState(
            incident_id=str(uuid.uuid4())
        )

    def update_flood(self, polygon: Optional[dict], severity: int, confidence: float):
        self.state.flood_polygon = polygon
        self.state.severity = severity
        self.state.confidence = confidence

        self._log_state_change("FLOOD_UPDATED")

    def add_mission(self, mission):
        self.state.missions[mission.mission_id] = mission
        self._log_state_change("MISSION_CREATED")

    def update_volunteer(self, volunteer):
        self.state.volunteers[volunteer.volunteer_id] = volunteer
        self._log_state_change("VOLUNTEER_UPDATED")

    def _log_state_change(self, action: str):
        self.state.timeline.append({
            "timestamp": datetime.utcnow(),
            "action": action
        })

    def get_state(self) -> IncidentState:
        return self.state