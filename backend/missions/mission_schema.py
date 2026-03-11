# backend/missions/mission_schema.py

from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum

class MissionType(str, Enum):
    CLUSTER = "CLUSTER"
    IMMEDIATE = "IMMEDIATE"


class Mission(BaseModel):

    mission_id: str
    type: MissionType  # ← THIS MUST BE EXACTLY "type"

    cluster_id: Optional[str] = None
    report: Optional[dict] = None

    priority: str
    status: str  # CREATED / ASSIGNED / EN_ROUTE / ACTIVE / COMPLETED

    assigned_volunteer: Optional[str] = None

    created_at: datetime