# backend/environmental/agent/schemas.py

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class WeatherSignal(BaseModel):
    station_id: str
    rainfall_mm: float
    river_level_m: float
    danger_level_m: float
    timestamp: datetime


class SatelliteSignal(BaseModel):
    polygon_geojson: Dict[str, Any]
    confidence: float
    water_extent_score: float = 0.0
    timestamp: datetime


class SocialSignal(BaseModel):
    report_id: str
    text: str
    lat: float
    lon: float
    urgency: int
    credibility: float
    timestamp: datetime


class DepthEstimationResult(BaseModel):
    estimated_depth_m: Optional[float] = None
    depth_model_used: bool = False
    confidence: float = 0.0


class FloodDetectionResult(BaseModel):
    detected: bool
    confidence: float
    severity: int
    trend: str
    polygon_geojson: Optional[Dict[str, Any]] = None
    evidence_refs: List[str] = Field(default_factory=list)
    risk_factors: List[str] = Field(default_factory=list)
    depth_result: Optional[DepthEstimationResult] = None
    timestamp: datetime