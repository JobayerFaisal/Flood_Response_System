# backend/environmental/publisher.py

from backend.core.event_types import EventTypes


class EnvironmentalPublisher:
    def __init__(self, event_bus):
        self.event_bus = event_bus

    def publish_weather(self, signal):
        payload = signal.model_dump()
        payload["timestamp"] = signal.timestamp.isoformat()
        self.event_bus.publish(EventTypes.WEATHER_UPDATE, payload)

    def publish_satellite(self, signal):
        self.event_bus.publish(
            EventTypes.SATELLITE_UPDATE,
            {
                "flood_polygon": signal.flood_polygon,
                "confidence": signal.confidence,
                "timestamp": signal.timestamp.isoformat(),
            }
        )

    def publish_social(self, signal):
        payload = signal.model_dump()
        payload["timestamp"] = signal.timestamp.isoformat()
        self.event_bus.publish(EventTypes.SOCIAL_REPORT_RECEIVED, payload)

    def publish_flood_detected(self, signal):
        self.event_bus.publish(
            EventTypes.FLOOD_DETECTED,
            {
                "confidence": signal.confidence,
                "severity": signal.severity,
                "polygon": signal.polygon,
                "evidence_refs": signal.evidence_refs,
                "timestamp": signal.timestamp.isoformat(),
            }
        )