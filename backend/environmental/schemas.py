# backend/environmental/schemas.py

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class WeatherSignal(BaseModel):
    station_id: str
    rainfall: float
    river_level: float
    danger_level: float
    timestamp: datetime


class SatelliteSignal(BaseModel):
    flood_polygon: Dict[str, Any]
    confidence: float
    timestamp: datetime


class SocialSignal(BaseModel):
    report_id: str
    text: str
    lat: float
    lon: float
    urgency: int
    credibility: float
    timestamp: datetime


class FloodDetectionSignal(BaseModel):
    confidence: float
    severity: int
    polygon: Optional[Dict[str, Any]] = None
    evidence_refs: List[str] = Field(default_factory=list)
    timestamp: datetime