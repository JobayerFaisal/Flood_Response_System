# backend/tests/test_environmental_agent.py

from datetime import datetime

from backend.core.event_bus import EventBus
from backend.core.incident_manager import IncidentManager
from backend.core.event_types import EventTypes
from backend.environmental.agent.environmental_detection_agent import (
    EnvironmentalDetectionAgent,
)



def main():
    # --------------------------------------------------
    # 1️⃣ Core system setup
    # --------------------------------------------------
    event_bus = EventBus()
    incident_manager = IncidentManager(event_bus)

    # --------------------------------------------------
    # 2️⃣ Register environmental detection agent
    # --------------------------------------------------
    environmental_agent = EnvironmentalDetectionAgent(
        event_bus,
        incident_manager
    )
    environmental_agent.register()

    # --------------------------------------------------
    # 3️⃣ Debug listeners
    # --------------------------------------------------
    def on_flood_detected(payload):
        print("\n✅ FLOOD_DETECTED EVENT")
        print(payload)

    def on_flood_updated(payload):
        print("\n✅ FLOOD_INTELLIGENCE_UPDATED EVENT")
        print(payload)

    event_bus.subscribe(EventTypes.FLOOD_DETECTED, on_flood_detected)
    event_bus.subscribe(EventTypes.FLOOD_INTELLIGENCE_UPDATED, on_flood_updated)

    # --------------------------------------------------
    # 4️⃣ Publish weather update
    # --------------------------------------------------
    event_bus.publish(
        EventTypes.WEATHER_UPDATE,
        {
            "station_id": "WS-001",
            "rainfall_mm": 135.0,
            "river_level_m": 8.2,
            "danger_level_m": 6.8,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )

    # --------------------------------------------------
    # 5️⃣ Publish satellite update
    # --------------------------------------------------
    event_bus.publish(
        EventTypes.SATELLITE_UPDATE,
        {
            "polygon_geojson": {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [[
                                [90.35, 23.72],
                                [90.40, 23.72],
                                [90.40, 23.77],
                                [90.35, 23.77],
                                [90.35, 23.72]
                            ]]
                        },
                        "properties": {
                            "zone": "Kaliganj"
                        }
                    }
                ]
            },
            "confidence": 0.91,
            "water_extent_score": 0.82,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )

    # --------------------------------------------------
    # 6️⃣ Publish social reports
    # --------------------------------------------------
    social_reports = [
        {
            "report_id": "R-1001",
            "text": "Water entered our house near Kaliganj school",
            "lat": 23.741,
            "lon": 90.382,
            "urgency": 4,
            "credibility": 0.88,
            "timestamp": datetime.utcnow().isoformat(),
        },
        {
            "report_id": "R-1002",
            "text": "People stuck on the roof, need rescue boat",
            "lat": 23.744,
            "lon": 90.386,
            "urgency": 5,
            "credibility": 0.93,
            "timestamp": datetime.utcnow().isoformat(),
        },
        {
            "report_id": "R-1003",
            "text": "Need medicine and dry food",
            "lat": 23.739,
            "lon": 90.379,
            "urgency": 3,
            "credibility": 0.81,
            "timestamp": datetime.utcnow().isoformat(),
        },
    ]

    for report in social_reports:
        event_bus.publish(EventTypes.SOCIAL_REPORT_RECEIVED, report)

    # --------------------------------------------------
    # 7️⃣ Inspect final incident state
    # --------------------------------------------------
    state = incident_manager.get_state()

    print("\n----- FINAL INCIDENT STATE -----")
    print(f"Incident ID: {state.incident_id}")
    print(f"Status: {state.status}")
    print(f"Severity: {state.severity}")
    print(f"Confidence: {state.confidence}")
    print(f"Flood Polygon Present: {state.flood_polygon is not None}")
    print(f"Reports Stored: {len(state.reports)}")
    print(f"Timeline Entries: {len(state.timeline)}")

    print("\n----- TIMELINE -----")
    for entry in state.timeline:
        print(entry)

    print("\n----- EVENT LOG -----")
    for event in event_bus.get_event_log():
        print(event)


if __name__ == "__main__":
    main()