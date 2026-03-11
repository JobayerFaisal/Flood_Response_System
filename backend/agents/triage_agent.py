# backend/agents/triage_agent.py

from backend.core.base_agent import BaseAgent
from backend.core.event_types import EventTypes
from backend.planning.clustering import cluster_reports


class TriageAgent(BaseAgent):

    CLUSTER_THRESHOLD = 3
    URGENCY_CRITICAL = 5
    CREDIBILITY_THRESHOLD = 0.8

    # -------------------------------------------------
    # Register Event Listener
    # -------------------------------------------------
    def register(self):
        self.event_bus.subscribe(
            EventTypes.SOCIAL_REPORT_RECEIVED,
            self.handle_report
        )

    # -------------------------------------------------
    # Handle Incoming Report
    # -------------------------------------------------
    def handle_report(self, payload: dict):

        state = self.incident_manager.get_state()

        if state is None:
            return

        # 1️⃣ Store report
        state.reports.append(payload)

        urgency = payload.get("urgency", 1)
        credibility = payload.get("credibility", 0)

        # -------------------------------------------------
        # 2️⃣ Immediate Escalation (Critical Override)
        # -------------------------------------------------
        if (
            urgency >= self.URGENCY_CRITICAL and
            credibility >= self.CREDIBILITY_THRESHOLD
        ):
            self.event_bus.publish(
                EventTypes.MISSION_REQUESTED,
                {
                    "type": "IMMEDIATE",
                    "report": payload,
                    "avg_urgency": urgency
                }
            )
            return

        # -------------------------------------------------
        # 3️⃣ Cluster Reports
        # -------------------------------------------------
        clustered = cluster_reports(state.reports)

        clusters = {}

        for r in clustered:
            cid = str(r.get("cluster_id", -1))
            clusters.setdefault(cid, [])
            clusters[cid].append(r)

        state.clusters = clusters

        # -------------------------------------------------
        # 4️⃣ Cluster Escalation Logic
        # -------------------------------------------------
        for cid, reports in clusters.items():

            if not reports:
                continue

            credible_reports = [
                r for r in reports
                if r.get("credibility", 0) >= self.CREDIBILITY_THRESHOLD
            ]

            avg_urgency = (
                sum(r.get("urgency", 1) for r in reports) / len(reports)
            )

            if (
                len(credible_reports) >= self.CLUSTER_THRESHOLD
                or avg_urgency >= 4
            ):
                self.event_bus.publish(
                    EventTypes.MISSION_REQUESTED,
                    {
                        "type": "CLUSTER",
                        "cluster_id": cid,
                        "size": len(reports),
                        "avg_urgency": avg_urgency
                    }
                )

        # -------------------------------------------------
        # 5️⃣ Notify Cluster Update
        # -------------------------------------------------
        self.event_bus.publish(
            EventTypes.CLUSTERS_UPDATED,
            {
                "cluster_count": len(clusters)
            }
        )