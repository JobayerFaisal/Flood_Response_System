# backend/environmental/adapter.py

from datetime import datetime
from backend.environmental.schemas import (
    WeatherSignal,
    SatelliteSignal,
    SocialSignal,
    FloodDetectionSignal,
)


class EnvironmentalAdapter:
    def __init__(self, teammate_agent):
        self.teammate_agent = teammate_agent

    def extract_weather(self, raw: dict) -> WeatherSignal:
        return WeatherSignal(
            station_id=str(raw.get("station_id", "unknown")),
            rainfall=float(raw.get("rainfall", 0)),
            river_level=float(raw.get("river_level", 0)),
            danger_level=float(raw.get("danger_level", 0)),
            timestamp=raw.get("timestamp", datetime.utcnow()),
        )

    def extract_satellite(self, raw: dict) -> SatelliteSignal:
        return SatelliteSignal(
            flood_polygon=raw.get("flood_polygon", {"type": "FeatureCollection", "features": []}),
            confidence=float(raw.get("confidence", 0)),
            timestamp=raw.get("timestamp", datetime.utcnow()),
        )

    def extract_social(self, raw: dict) -> SocialSignal:
        return SocialSignal(
            report_id=str(raw.get("report_id", "unknown")),
            text=str(raw.get("text", "")),
            lat=float(raw.get("lat", 0)),
            lon=float(raw.get("lon", 0)),
            urgency=int(raw.get("urgency", 1)),
            credibility=float(raw.get("credibility", 0.5)),
            timestamp=raw.get("timestamp", datetime.utcnow()),
        )

    def extract_flood_detection(self, raw: dict) -> FloodDetectionSignal:
        return FloodDetectionSignal(
            confidence=float(raw.get("confidence", 0)),
            severity=int(raw.get("severity", 1)),
            polygon=raw.get("polygon"),
            evidence_refs=raw.get("evidence_refs", []),
            timestamp=raw.get("timestamp", datetime.utcnow()),
        )
