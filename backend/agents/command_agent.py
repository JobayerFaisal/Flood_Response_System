# backend/agents/command_agent.py

from backend.core.base_agent import BaseAgent
from backend.core.event_types import EventTypes
from backend.missions.mission_manager import MissionManager


class CommandAgent(BaseAgent):

    def __init__(self, event_bus, incident_manager, global_learning_engine):
        super().__init__(event_bus, incident_manager)
        self.mission_manager = MissionManager(incident_manager)
        self.global_learning_engine = global_learning_engine

    # -------------------------------------------------
    # Register to Event Bus
    # -------------------------------------------------
    def register(self):
        self.event_bus.subscribe(
            EventTypes.MISSION_REQUESTED,
            self.handle_mission_request
        )

    # -------------------------------------------------
    # Handle Mission Request
    # -------------------------------------------------
    def handle_mission_request(self, payload: dict):

        mission = self.mission_manager.create_mission(payload)

        best_volunteer = self._select_best_volunteer(mission)

        if not best_volunteer:
            return

        self.mission_manager.assign_volunteer(
            mission_id=mission.mission_id,
            volunteer_id=best_volunteer.volunteer_id
        )

        # Record assignment globally
        self.global_learning_engine.record_status(
            best_volunteer.volunteer_id,
            mission.mission_id,
            "ASSIGNED"
        )

        self.event_bus.publish(
            EventTypes.MISSION_ASSIGNED,
            {
                "mission_id": mission.mission_id,
                "volunteer_id": best_volunteer.volunteer_id
            }
        )

    # -------------------------------------------------
    # Volunteer Ranking Logic
    # -------------------------------------------------
    def _select_best_volunteer(self, mission):

        state = self.incident_manager.get_state()

        available_volunteers = [
            v for v in state.volunteers.values()
            if v.available
        ]

        if not available_volunteers:
            return None

        scored = []

        for volunteer in available_volunteers:

            score = 0

            # 1️⃣ Distance
            mission_location = self._extract_mission_location(mission)

            if mission_location:
                distance = self._distance(
                    mission_location,
                    volunteer.location
                )
                score -= distance

            # 2️⃣ Skill match
            required_skill = self._infer_required_skill(mission)

            if required_skill in volunteer.skills:
                score += 10

            # 3️⃣ Equipment match
            if (
                mission.type.value == "IMMEDIATE"
                and "boat" in volunteer.equipment
            ):
                score += 5

            # 4️⃣ Persistent Global Learning Adjustment
            success_rate = self.global_learning_engine.get_weighted_success_score(
                volunteer.volunteer_id
            )

            score += success_rate * 10  # Learning weight

            scored.append((score, volunteer))

        scored.sort(key=lambda x: x[0], reverse=True)

        best_volunteer = scored[0][1]

        best_volunteer.available = False

        return best_volunteer

    # -------------------------------------------------
    # Helpers
    # -------------------------------------------------
    def _extract_mission_location(self, mission):

        if mission.report:
            return (
                mission.report.get("lat"),
                mission.report.get("lon")
            )

        return None

    def _infer_required_skill(self, mission):

        if mission.type.value == "IMMEDIATE":
            return "rescue"

        return "general"

    def _distance(self, loc1, loc2):

        if not loc1 or not loc2:
            return 999

        lat1, lon1 = loc1
        lat2, lon2 = loc2

        return ((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2) ** 0.5