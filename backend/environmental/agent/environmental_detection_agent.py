# backend/environmental/agent/environmental_detection_agent.py

from typing import List, Optional
from datetime import datetime

from backend.core.base_agent import BaseAgent
from backend.core.event_types import EventTypes
from backend.environmental.agent.schemas import (
    WeatherSignal,
    SatelliteSignal,
    SocialSignal,
)
from backend.environmental.agent.flood_risk_engine import FloodRiskEngine
from backend.environmental.agent.publisher import EnvironmentalPublisher


class EnvironmentalDetectionAgent(BaseAgent):
    """
    Event-driven environmental intelligence agent.

    Listens to:
    - WEATHER_UPDATE
    - SATELLITE_UPDATE
    - SOCIAL_REPORT_RECEIVED

    Produces:
    - FLOOD_DETECTED (only on first threshold crossing)
    - FLOOD_INTELLIGENCE_UPDATED
    """

    def __init__(self, event_bus, incident_manager):
        super().__init__(event_bus, incident_manager)
        self.risk_engine = FloodRiskEngine()
        self.publisher = EnvironmentalPublisher(event_bus)

        self.latest_weather: Optional[WeatherSignal] = None
        self.latest_satellite: Optional[SatelliteSignal] = None
        self.social_reports: List[SocialSignal] = []
        self.flood_already_detected = False

    # -------------------------------------------------
    # Register
    # -------------------------------------------------
    def register(self):
        self.event_bus.subscribe(EventTypes.WEATHER_UPDATE, self.handle_weather)
        self.event_bus.subscribe(EventTypes.SATELLITE_UPDATE, self.handle_satellite)
        self.event_bus.subscribe(
            EventTypes.SOCIAL_REPORT_RECEIVED,
            self.handle_social_report
        )

    # -------------------------------------------------
    # Handlers
    # -------------------------------------------------
    def handle_weather(self, payload: dict):
        try:
            self.latest_weather = WeatherSignal(
                station_id=str(payload.get("station_id", "unknown")),
                rainfall_mm=float(payload.get("rainfall_mm", payload.get("rainfall", 0.0))),
                river_level_m=float(payload.get("river_level_m", payload.get("river_level", 0.0))),
                danger_level_m=float(payload.get("danger_level_m", payload.get("danger_level", 0.0))),
                timestamp=self._parse_timestamp(payload.get("timestamp")),
            )
            self._run_detection(evidence_ref=self.latest_weather.station_id)
        except Exception as e:
            print(f"EnvironmentalDetectionAgent.handle_weather failed: {e}")

    def handle_satellite(self, payload: dict):
        try:
            self.latest_satellite = SatelliteSignal(
                polygon_geojson=payload.get(
                    "polygon_geojson",
                    payload.get("flood_polygon", {"type": "FeatureCollection", "features": []})
                ),
                confidence=float(payload.get("confidence", 0.0)),
                water_extent_score=float(payload.get("water_extent_score", 0.0)),
                timestamp=self._parse_timestamp(payload.get("timestamp")),
            )
            self._run_detection(evidence_ref="SATELLITE")
        except Exception as e:
            print(f"EnvironmentalDetectionAgent.handle_satellite failed: {e}")

    def handle_social_report(self, payload: dict):
        try:
            report = SocialSignal(
                report_id=str(payload.get("report_id", "unknown")),
                text=str(payload.get("text", "")),
                lat=float(payload.get("lat", 0.0)),
                lon=float(payload.get("lon", 0.0)),
                urgency=int(payload.get("urgency", 1)),
                credibility=float(payload.get("credibility", 0.5)),
                timestamp=self._parse_timestamp(payload.get("timestamp")),
            )

            # Store in agent-local rolling buffer
            self.social_reports.append(report)
            if len(self.social_reports) > 100:
                self.social_reports = self.social_reports[-100:]

            # Store in global incident state
            state = self.incident_manager.get_state()
            state.reports.append(report.model_dump())

            self._run_detection(evidence_ref=report.report_id)

        except Exception as e:
            print(f"EnvironmentalDetectionAgent.handle_social_report failed: {e}")

    # -------------------------------------------------
    # Core Detection
    # -------------------------------------------------
    def _run_detection(self, evidence_ref: Optional[str] = None):
        evidence_refs = []

        if self.latest_weather is not None:
            evidence_refs.append(self.latest_weather.station_id)

        if self.latest_satellite is not None:
            evidence_refs.append("SATELLITE")

        if evidence_ref and evidence_ref not in evidence_refs:
            evidence_refs.append(evidence_ref)

        result = self.risk_engine.detect(
            weather=self.latest_weather,
            satellite=self.latest_satellite,
            social_reports=self.social_reports,
            evidence_refs=evidence_refs,
        )

        # Update central incident state
        state = self.incident_manager.get_state()
        state.flood_polygon = result.polygon_geojson
        state.severity = result.severity
        state.confidence = result.confidence

        state.timeline.append({
            "event": "ENVIRONMENTAL_DETECTION_UPDATED",
            "confidence": result.confidence,
            "severity": result.severity,
            "detected": result.detected,
            "risk_factors": result.risk_factors,
            "timestamp": result.timestamp.isoformat(),
        })

        # One-time FLOOD_DETECTED, continuous FLOOD_INTELLIGENCE_UPDATED
        if result.detected and not self.flood_already_detected:
            self.publisher.publish_detection(result)
            self.flood_already_detected = True
        else:
            self.event_bus.publish(
                EventTypes.FLOOD_INTELLIGENCE_UPDATED,
                {
                    "detected": result.detected,
                    "confidence": result.confidence,
                    "severity": result.severity,
                    "trend": result.trend,
                    "polygon_geojson": result.polygon_geojson,
                    "evidence_refs": result.evidence_refs,
                    "risk_factors": result.risk_factors,
                    "depth_result": (
                        result.depth_result.model_dump()
                        if result.depth_result else None
                    ),
                    "timestamp": result.timestamp.isoformat(),
                }
            )

    # -------------------------------------------------
    # Helpers
    # -------------------------------------------------
    def _parse_timestamp(self, value):
        if value is None:
            return datetime.utcnow()

        if isinstance(value, datetime):
            return value

        try:
            return datetime.fromisoformat(str(value))
        except Exception:
            return datetime.utcnow()