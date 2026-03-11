# backend/missions/mission_manager.py

import uuid
from datetime import datetime
from typing import Optional

from backend.missions.mission_schema import Mission, MissionType


class MissionManager:

    def __init__(self, incident_manager):
        self.incident_manager = incident_manager

    # --------------------------------------------------
    # Create Mission (Triggered by MISSION_REQUESTED)
    # --------------------------------------------------
    def create_mission(self, payload: dict) -> Mission:

        if not isinstance(payload, dict):
            raise ValueError("Mission payload must be a dictionary.")

        mission_type_raw = payload.get("type")

        if mission_type_raw is None:
            raise ValueError("Mission type is required.")

        try:
            mission_type = MissionType(mission_type_raw)
        except ValueError:
            raise ValueError(f"Invalid mission type: {mission_type_raw}")

        state = self.incident_manager.get_state()

        if state is None:
            raise RuntimeError("Incident state not initialized.")

        # Optional: prevent duplicate cluster missions
        cluster_id = payload.get("cluster_id")
        if cluster_id:
            for m in state.missions.values():
                if (
                    m.cluster_id == cluster_id
                    and m.status in ["CREATED", "ASSIGNED", "EN_ROUTE", "ACTIVE"]
                ):
                    # Mission already exists for this cluster
                    return m

        mission = Mission(
            mission_id=str(uuid.uuid4()),
            type=mission_type,
            cluster_id=cluster_id,
            report=payload.get("report"),
            priority=self._determine_priority(payload),
            status="CREATED",
            assigned_volunteer=None,
            created_at=datetime.utcnow(),
        )

        state.missions[mission.mission_id] = mission

        return mission

    # --------------------------------------------------
    # Assign Volunteer
    # --------------------------------------------------
    def assign_volunteer(self, mission_id: str, volunteer_id: str) -> Mission:

        state = self.incident_manager.get_state()

        if state is None:
            raise RuntimeError("Incident state not initialized.")

        mission: Optional[Mission] = state.missions.get(mission_id)

        if mission is None:
            raise ValueError(f"Mission {mission_id} not found.")

        if mission.status not in ["CREATED"]:
            raise ValueError(
                f"Mission {mission_id} cannot be assigned in status {mission.status}"
            )

        mission.assigned_volunteer = volunteer_id
        mission.status = "ASSIGNED"

        return mission

    # --------------------------------------------------
    # Update Mission Status
    # --------------------------------------------------
    def update_status(self, mission_id: str, new_status: str) -> Mission:

        state = self.incident_manager.get_state()

        if state is None:
            raise RuntimeError("Incident state not initialized.")

        mission: Optional[Mission] = state.missions.get(mission_id)

        if mission is None:
            raise ValueError(f"Mission {mission_id} not found.")

        allowed_status = ["CREATED", "ASSIGNED", "EN_ROUTE", "ACTIVE", "COMPLETED"]

        if new_status not in allowed_status:
            raise ValueError(f"Invalid mission status: {new_status}")

        mission.status = new_status

        return mission

    # --------------------------------------------------
    # Priority Logic
    # --------------------------------------------------
    def _determine_priority(self, payload: dict) -> str:

        mission_type_raw = payload.get("type")

        if mission_type_raw == MissionType.IMMEDIATE.value:
            return "CRITICAL"

        avg_urgency = payload.get("avg_urgency", 3)

        if avg_urgency >= 4:
            return "HIGH"

        if avg_urgency >= 2:
            return "MEDIUM"

        return "LOW"