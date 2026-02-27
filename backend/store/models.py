# backend/store/models.py

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from .db import Base
from datetime import datetime


class Scenario(Base):
    __tablename__ = "scenarios"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    seed = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)


class FloodEventModel(Base):
    __tablename__ = "flood_events"

    id = Column(Integer, primary_key=True)

    scenario_id = Column(Integer, ForeignKey("scenarios.id"))

    # 🔥 NEW CORE IDENTIFIERS
    event_id = Column(String, unique=True, nullable=False)
    timestamp_start = Column(DateTime)
    timestamp_current = Column(DateTime)

    confidence = Column(Float)
    severity = Column(Integer)
    trend = Column(String)

    # 🔥 NEW SPATIAL ANALYTICS
    area = Column(Float)
    bbox = Column(JSONB)
    centroid = Column(JSONB)

    # Existing
    geojson = Column(JSONB)
    hazards = Column(JSONB)
    impact_estimates = Column(JSONB)
    evidence_refs = Column(JSONB)

    created_at = Column(DateTime, default=datetime.utcnow)