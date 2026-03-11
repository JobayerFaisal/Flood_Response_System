# backend/memory/performance_tracker.py

from collections import defaultdict


class PerformanceTracker:

    def __init__(self):
        self.volunteer_stats = defaultdict(lambda: {
            "missions_assigned": 0,
            "missions_completed": 0,
            "missions_failed": 0,
        })

    def record_assignment(self, volunteer_id: str):
        self.volunteer_stats[volunteer_id]["missions_assigned"] += 1

    def record_completion(self, volunteer_id: str):
        self.volunteer_stats[volunteer_id]["missions_completed"] += 1

    def record_failure(self, volunteer_id: str):
        self.volunteer_stats[volunteer_id]["missions_failed"] += 1

    def get_success_rate(self, volunteer_id: str) -> float:
        stats = self.volunteer_stats[volunteer_id]
        assigned = stats["missions_assigned"]

        if assigned == 0:
            return 1.0  # neutral default

        return stats["missions_completed"] / assigned