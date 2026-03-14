# backend/environmental/agent/flood_risk_engine.py

from datetime import datetime
from typing import List, Optional

from backend.environmental.agent.config import (
    WEATHER_WEIGHT,
    SATELLITE_WEIGHT,
    SOCIAL_WEIGHT,
    FLOOD_DETECTION_THRESHOLD,
    SEVERITY_LOW_THRESHOLD,
    SEVERITY_MEDIUM_THRESHOLD,
    SEVERITY_HIGH_THRESHOLD,
    SEVERITY_CRITICAL_THRESHOLD,
    DEFAULT_TREND,
)
from backend.environmental.agent.schemas import (
    WeatherSignal,
    SatelliteSignal,
    SocialSignal,
    FloodDetectionResult,
)
from backend.environmental.agent.depth_engine import DepthEngine


class FloodRiskEngine:
    def __init__(self):
        self.depth_engine = DepthEngine()

    def analyze_weather(self, weather: Optional[WeatherSignal]) -> dict:
        if weather is None:
            return {"rainfall_score": 0.0, "river_score": 0.0, "weather_score": 0.0}

        rainfall_score = min(weather.rainfall_mm / 150.0, 1.0)

        exceedance = max(weather.river_level_m - weather.danger_level_m, 0.0)
        river_score = min(exceedance / 3.0, 1.0)

        weather_score = (rainfall_score * 0.6) + (river_score * 0.4)

        return {
            "rainfall_score": rainfall_score,
            "river_score": river_score,
            "weather_score": round(weather_score, 4),
        }

    def analyze_satellite(self, satellite: Optional[SatelliteSignal]) -> dict:
        if satellite is None:
            return {
                "satellite_score": 0.0,
                "water_extent_score": 0.0,
                "polygon_geojson": None,
            }

        satellite_score = min(float(satellite.confidence), 1.0)
        extent_score = min(float(satellite.water_extent_score), 1.0)

        combined = (satellite_score * 0.7) + (extent_score * 0.3)

        return {
            "satellite_score": round(combined, 4),
            "water_extent_score": extent_score,
            "polygon_geojson": satellite.polygon_geojson,
        }

    def analyze_social(self, social_reports: List[SocialSignal]) -> dict:
        if not social_reports:
            return {"social_score": 0.0, "credible_count": 0, "avg_urgency": 0.0}

        credible_reports = [r for r in social_reports if r.credibility >= 0.7]
        credible_count = len(credible_reports)

        avg_urgency = (
            sum(r.urgency for r in credible_reports) / credible_count
            if credible_count > 0 else 0.0
        )

        density_score = min(credible_count / 20.0, 1.0)
        urgency_score = min(avg_urgency / 5.0, 1.0)

        social_score = (density_score * 0.5) + (urgency_score * 0.5)

        return {
            "social_score": round(social_score, 4),
            "credible_count": credible_count,
            "avg_urgency": round(avg_urgency, 3),
        }

    def estimate_severity(self, confidence: float) -> int:
        if confidence >= SEVERITY_CRITICAL_THRESHOLD:
            return 5
        if confidence >= SEVERITY_HIGH_THRESHOLD:
            return 4
        if confidence >= SEVERITY_MEDIUM_THRESHOLD:
            return 3
        if confidence >= SEVERITY_LOW_THRESHOLD:
            return 2
        return 1

    def infer_risk_factors(
        self,
        weather_features: dict,
        satellite_features: dict,
        social_features: dict,
    ) -> list[str]:
        risks = []

        if weather_features.get("river_score", 0) > 0.6:
            risks.append("river_overflow")

        if satellite_features.get("water_extent_score", 0) > 0.5:
            risks.append("water_extent_growth")

        if social_features.get("avg_urgency", 0) >= 4:
            risks.append("trapped_households")

        if social_features.get("credible_count", 0) >= 5:
            risks.append("community_distress_surge")

        return risks

    def detect(
        self,
        weather: Optional[WeatherSignal],
        satellite: Optional[SatelliteSignal],
        social_reports: List[SocialSignal],
        evidence_refs: Optional[List[str]] = None,
    ) -> FloodDetectionResult:
        evidence_refs = evidence_refs or []

        weather_features = self.analyze_weather(weather)
        satellite_features = self.analyze_satellite(satellite)
        social_features = self.analyze_social(social_reports)

        total_confidence = (
            weather_features["weather_score"] * WEATHER_WEIGHT
            + satellite_features["satellite_score"] * SATELLITE_WEIGHT
            + social_features["social_score"] * SOCIAL_WEIGHT
        )

        total_confidence = round(min(total_confidence, 1.0), 4)
        detected = total_confidence >= FLOOD_DETECTION_THRESHOLD
        severity = self.estimate_severity(total_confidence)

        # depth_result = self.depth_engine.predict_depth(
        #     weather_features=weather_features,
        #     satellite_features=satellite_features,
        #     social_features=social_features,
        # )
        depth_result = None

        risk_factors = self.infer_risk_factors(
            weather_features,
            satellite_features,
            social_features,
        )

        polygon_geojson = satellite_features.get("polygon_geojson")

        return FloodDetectionResult(
            detected=detected,
            confidence=total_confidence,
            severity=severity,
            trend=DEFAULT_TREND,
            polygon_geojson=polygon_geojson,
            evidence_refs=evidence_refs,
            risk_factors=risk_factors,
            depth_result=depth_result,
            timestamp=datetime.utcnow(),
        )