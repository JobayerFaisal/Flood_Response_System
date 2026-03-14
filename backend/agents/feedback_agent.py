# backend/agents/feedback_agent.py

from backend.core.base_agent import BaseAgent
from backend.core.event_types import EventTypes


class FeedbackAgent(BaseAgent):

    def __init__(self, event_bus, incident_manager, global_learning_engine):
        super().__init__(event_bus, incident_manager)
        self.global_learning_engine = global_learning_engine

    # -------------------------------------------------
    # Register to Event Bus
    # -------------------------------------------------
    def register(self):
        self.event_bus.subscribe(
            EventTypes.VOLUNTEER_REPORT_RECEIVED,
            self.handle_volunteer_feedback
        )

    # -------------------------------------------------
    # Handle Volunteer Feedback
    # -------------------------------------------------
    def handle_volunteer_feedback(self, payload: dict):

        state = self.incident_manager.get_state()

        mission_id = payload.get("mission_id")
        new_status = payload.get("status")

        mission = state.missions.get(mission_id)

        if not mission:
            return

        old_status = mission.status
        mission.status = new_status

        volunteer_id = mission.assigned_volunteer

        # -------------------------------------------------
        # 1️⃣ Record lifecycle into global learning memory
        # -------------------------------------------------
        if volunteer_id and mission_id and new_status:
            self.global_learning_engine.record_status(
                volunteer_id=volunteer_id,
                mission_id=mission_id,
                status=new_status
            )

        # -------------------------------------------------
        # 2️⃣ Escalate Severity (Controlled)
        # -------------------------------------------------
        if payload.get("medical_emergency"):

            previous_severity = state.severity or 1
            state.severity = min(previous_severity + 1, 5)

            if state.severity != previous_severity:
                self.event_bus.publish(
                    EventTypes.FLOOD_INTELLIGENCE_UPDATED,
                    {
                        "incident_id": state.incident_id,
                        "new_severity": state.severity
                    }
                )

        # -------------------------------------------------
        # 3️⃣ Mission Failure → Trigger AI Decision Layer
        # -------------------------------------------------
        if new_status == "FAILED":
            self.event_bus.publish(
                EventTypes.MISSION_FAILED,
                {
                    "mission_id": mission_id,
                    "reason": payload.get("reason", "Unknown"),
                    "volunteer_id": volunteer_id,
                    "details": payload
                }
            )

        # -------------------------------------------------
        # 4️⃣ Mission Completed → Free Volunteer
        # -------------------------------------------------
        if new_status == "COMPLETED" and volunteer_id:
            if volunteer_id in state.volunteers:
                state.volunteers[volunteer_id].available = True

        # -------------------------------------------------
        # 5️⃣ Log Timeline (Critical for Replay)
        # -------------------------------------------------
        state.timeline.append({
            "event": "MISSION_STATUS_UPDATED",
            "mission_id": mission_id,
            "from": old_status,
            "to": new_status,
            "volunteer_id": volunteer_id
        })