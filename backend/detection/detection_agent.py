# backend/detection/detection_agent.py

from git import Optional

from backend.core.base_agent import BaseAgent
from backend.core.event_types import EventTypes


class DetectionAgent(BaseAgent):

    def register(self):
        self.event_bus.subscribe(EventTypes.WEATHER_UPDATE, self.handle_weather)
        self.event_bus.subscribe(EventTypes.SATELLITE_UPDATE, self.handle_satellite)

    def handle_weather(self, payload: dict):
        """
        Payload example:
        {
            "rainfall": 120,
            "river_level": 7.8,
            "danger_level": 6.5
        }
        """

        rainfall = payload.get("rainfall", 0)
        river_level = payload.get("river_level", 0)
        danger_level = payload.get("danger_level", 0)

        # Simple rule-based detection
        if rainfall > 100 and river_level > danger_level:
            self._confirm_flood(confidence=0.8)

    def handle_satellite(self, payload: dict):
        """
        Payload example:
        {
            "flood_polygon": {...},
            "confidence": 0.92
        }
        """

        polygon = payload.get("flood_polygon")
        confidence = payload.get("confidence", 0)

        if polygon and confidence > 0.85:
            self._confirm_flood(confidence=confidence, polygon=polygon)

    def _confirm_flood(self, confidence: float, polygon: Optional[dict] = None):
        severity = 4 if confidence > 0.85 else 3

        # Update central state
        self.incident_manager.update_flood(
            polygon=polygon,
            severity=severity,
            confidence=confidence
        )

        # Emit event
        self.event_bus.publish(
            EventTypes.FLOOD_CONFIRMED,
            {
                "severity": severity,
                "confidence": confidence,
                "polygon": polygon
            }
        )