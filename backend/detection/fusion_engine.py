# backend/detection/fusion_engine.py

from datetime import datetime
import uuid
from shapely.geometry import mapping
from backend.schemas.flood_event import FloodEvent, ImpactEstimates


def detect_flood(step_data):

    polygon = step_data["polygon"]
    area = polygon.area
    centroid = polygon.centroid
    bbox = list(polygon.bounds)

    confidence = min(
        1.0,
        0.4 * step_data["weather_score"] +
        0.3 * step_data["social_score"] +
        0.3 * step_data["satellite_score"]
    )

    # Area-based severity
    if area < 0.01:
        severity = 2
    elif area < 0.02:
        severity = 3
    elif area < 0.03:
        severity = 4
    else:
        severity = 5

    geojson = {
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "geometry": mapping(polygon),
            "properties": {}
        }]
    }

    event = FloodEvent(
        event_id=str(uuid.uuid4()),
        timestamp_start=datetime.utcnow(),
        timestamp_current=datetime.utcnow(),
        confidence=confidence,
        severity=severity,
        trend="rising",
        affected_area_geojson=geojson,
        area=area,
        bbox=bbox,
        centroid=(centroid.y, centroid.x),
        evidence_refs=step_data["evidence_refs"],
        impact_estimates=ImpactEstimates(
            people_exposed=int(area * 100000),
            houses_affected=int(area * 30000)
        ),
        hazards=["road_blocked", "contamination_risk"]
    )

    return event