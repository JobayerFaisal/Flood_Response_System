# backend/store/repositories.py

from backend.store.models import FloodEventModel, Scenario
from backend.store.db import SessionLocal


def save_event(event, scenario_name, seed):
    session = SessionLocal()

    try:
        # Find or create scenario
        scenario = session.query(Scenario).filter_by(
            name=scenario_name,
            seed=seed
        ).first()

        if not scenario:
            scenario = Scenario(name=scenario_name, seed=seed)
            session.add(scenario)
            session.commit()

        model = FloodEventModel(
            scenario_id=scenario.id,
            event_id=event.event_id,
            timestamp_start=event.timestamp_start,
            timestamp_current=event.timestamp_current,
            confidence=event.confidence,
            severity=event.severity,
            trend=event.trend,
            area=event.area,
            bbox=event.bbox,
            centroid=event.centroid,
            geojson=event.affected_area_geojson,
            hazards=event.hazards,
            impact_estimates=event.impact_estimates.model_dump(),
            evidence_refs=event.evidence_refs
        )

        session.add(model)
        session.commit()

    finally:
        session.close()