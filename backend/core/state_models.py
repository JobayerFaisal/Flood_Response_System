# backend/core/state_models.py

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Tuple

from backend.missions.mission_schema import Mission


class Volunteer(BaseModel):
    volunteer_id: str
    location: Tuple[float, float]
    skills: List[str]
    equipment: List[str]
    available: bool = True
    division: str = "Sylhet"
    district: str = "Sylhet"


class Resource(BaseModel):
    resource_id: str
    location: Tuple[float, float]
    type: str
    quantity: int


class IncidentState(BaseModel):
    incident_id: str
    status: str = "ACTIVE"

    flood_polygon: Optional[dict] = None
    severity: Optional[int] = None
    confidence: Optional[float] = None

    clusters: Dict[str, dict] = Field(default_factory=dict)

    missions: Dict[str, Mission] = Field(default_factory=dict)
    volunteers: Dict[str, Volunteer] = Field(default_factory=dict)
    resources: Dict[str, Resource] = Field(default_factory=dict)

    timeline: List[dict] = Field(default_factory=list)
    reports: List[dict] = Field(default_factory=list)