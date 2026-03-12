# backend/environmental/run_adapter.py

from backend.core.event_bus import EventBus
from backend.environmental.adapter import EnvironmentalAdapter
from backend.environmental.publisher import EnvironmentalPublisher


def run_environmental_pipeline(event_bus: EventBus):
    # teammate_agent = EnvironmentalAgent(...)
    teammate_agent = None

    adapter = EnvironmentalAdapter(teammate_agent)
    publisher = EnvironmentalPublisher(event_bus)

    # Replace these with real outputs from teammate agent
    raw_weather = {
        "station_id": "WS1",
        "rainfall": 120,
        "river_level": 7.8,
        "danger_level": 6.5,
    }
    raw_satellite = {
        "flood_polygon": {"type": "FeatureCollection", "features": []},
        "confidence": 0.91,
    }
    raw_social = {
        "report_id": "R100",
        "text": "People stuck near school",
        "lat": 23.75,
        "lon": 90.40,
        "urgency": 5,
        "credibility": 0.92,
    }
    raw_flood = {
        "confidence": 0.91,
        "severity": 4,
        "polygon": {"type": "FeatureCollection", "features": []},
        "evidence_refs": ["WS1", "SAT_TILE_1", "R100"],
    }

    publisher.publish_weather(adapter.extract_weather(raw_weather))
    publisher.publish_satellite(adapter.extract_satellite(raw_satellite))
    publisher.publish_social(adapter.extract_social(raw_social))
    publisher.publish_flood_detected(adapter.extract_flood_detection(raw_flood))