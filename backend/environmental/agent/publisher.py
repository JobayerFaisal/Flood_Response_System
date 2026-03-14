# backend/environmental/agent/publisher.py

from backend.core.event_types import EventTypes
from backend.environmental.agent.schemas import FloodDetectionResult


class EnvironmentalPublisher:
    def __init__(self, event_bus):
        self.event_bus = event_bus

    def publish_detection(self, result: FloodDetectionResult):
        payload = {
            "detected": result.detected,
            "confidence": result.confidence,
            "severity": result.severity,
            "trend": result.trend,
            "polygon_geojson": result.polygon_geojson,
            "evidence_refs": result.evidence_refs,
            "risk_factors": result.risk_factors,
            "depth_result": (
                result.depth_result.model_dump() if result.depth_result else None
            ),
            "timestamp": result.timestamp.isoformat(),
        }

        if result.detected:
            self.event_bus.publish(EventTypes.FLOOD_DETECTED, payload)

        self.event_bus.publish(EventTypes.FLOOD_INTELLIGENCE_UPDATED, payload)