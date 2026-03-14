# backend/agents/flood_response_coordinator.py

from backend.core.base_agent import BaseAgent
from backend.core.event_types import EventTypes


class FloodResponseCoordinator(BaseAgent):
    """
    Bridges environmental intelligence into operational incident response.
    """

    def register(self):
        self.event_bus.subscribe(
            EventTypes.FLOOD_DETECTED,
            self.handle_flood_detected
        )
        self.event_bus.subscribe(
            EventTypes.FLOOD_INTELLIGENCE_UPDATED,
            self.handle_flood_updated
        )

    def handle_flood_detected(self, payload: dict):
        state = self.incident_manager.get_state()

        state.status = "FLOOD_RESPONSE_ACTIVE"
        state.flood_polygon = payload.get("polygon_geojson")
        state.severity = payload.get("severity")
        state.confidence = payload.get("confidence")

        state.timeline.append({
            "event": "FLOOD_RESPONSE_ACTIVATED",
            "severity": state.severity,
            "confidence": state.confidence,
            "division": self._extract_division(payload.get("polygon_geojson")),
            "district": self._extract_district(payload.get("polygon_geojson")),
            "timestamp": payload.get("timestamp"),
        })

        severity = payload.get("severity", 1)
        risk_factors = payload.get("risk_factors", [])

        if severity >= 3:
            self.event_bus.publish(
                EventTypes.MISSION_REQUESTED,
                {
                    "type": "CLUSTER",
                    "cluster_id": "ENV_INITIAL",
                    "avg_urgency": 4 if "trapped_households" in risk_factors else 3,
                    "report": {
                        "lat": self._extract_centroid_lat(payload.get("polygon_geojson")),
                        "lon": self._extract_centroid_lon(payload.get("polygon_geojson")),
                        "source": "ENVIRONMENTAL_DETECTION",
                        "division": self._extract_division(payload.get("polygon_geojson")),
                        "district": self._extract_district(payload.get("polygon_geojson")),
                    }
                }
            )

    def handle_flood_updated(self, payload: dict):
        state = self.incident_manager.get_state()

        state.flood_polygon = payload.get("polygon_geojson")
        state.severity = payload.get("severity")
        state.confidence = payload.get("confidence")

        state.timeline.append({
            "event": "FLOOD_RESPONSE_UPDATED",
            "severity": state.severity,
            "confidence": state.confidence,
            "risk_factors": payload.get("risk_factors", []),
            "division": self._extract_division(payload.get("polygon_geojson")),
            "district": self._extract_district(payload.get("polygon_geojson")),
            "timestamp": payload.get("timestamp"),
        })

    def _extract_centroid_lat(self, polygon_geojson):
        try:
            coords = polygon_geojson["features"][0]["geometry"]["coordinates"][0]
            lats = [pt[1] for pt in coords]
            return sum(lats) / len(lats)
        except Exception:
            return 0.0

    def _extract_centroid_lon(self, polygon_geojson):
        try:
            coords = polygon_geojson["features"][0]["geometry"]["coordinates"][0]
            lons = [pt[0] for pt in coords]
            return sum(lons) / len(lons)
        except Exception:
            return 0.0

    def _extract_division(self, polygon_geojson):
        try:
            return polygon_geojson["features"][0]["properties"].get("division", "Sylhet")
        except Exception:
            return "Sylhet"

    def _extract_district(self, polygon_geojson):
        try:
            return polygon_geojson["features"][0]["properties"].get("district", "Sylhet")
        except Exception:
            return "Sylhet"