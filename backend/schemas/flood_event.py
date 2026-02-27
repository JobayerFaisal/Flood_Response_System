# backend/schemas/flood_event.py

from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Tuple, Optional


class ImpactEstimates(BaseModel):
    people_exposed: int
    houses_affected: int


class FloodEvent(BaseModel):
    event_id: str
    timestamp_start: datetime
    timestamp_current: datetime

    confidence: float
    severity: int
    trend: str

    affected_area_geojson: Dict

    # 🔥 NEW FIELDS
    area: float
    bbox: List[float]
    centroid: Tuple[float, float]

    evidence_refs: Dict
    impact_estimates: ImpactEstimates
    hazards: List[str]