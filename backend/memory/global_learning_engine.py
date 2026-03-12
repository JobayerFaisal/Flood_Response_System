import math
from datetime import datetime
from backend.memory.persistent_store import PersistentStore


class GlobalLearningEngine:

    def __init__(self, store: PersistentStore, decay_half_life_days=30):
        self.store = store
        self.decay_half_life_days = decay_half_life_days

    def record_completion(self, volunteer_id: str):
        self.store.record_outcome(volunteer_id, "COMPLETED")

    def record_failure(self, volunteer_id: str):
        self.store.record_outcome(volunteer_id, "FAILED")

    def record_status(self, volunteer_id: str, mission_id: str, status: str):
        self.store.record_lifecycle(volunteer_id, mission_id, status)

    def get_weighted_success_score(self, volunteer_id: str) -> float:

        history = self.store.get_lifecycle_history(volunteer_id)

        if not history:
            return 1.0

        total_weight = 0
        success_weight = 0

        now = datetime.utcnow()

        for mission_id, status, timestamp_str in history:

            timestamp = datetime.fromisoformat(timestamp_str)
            days_old = (now - timestamp).days

            weight = math.exp(-math.log(2) * days_old / self.decay_half_life_days)

            total_weight += weight

            if status == "COMPLETED":
                success_weight += weight

            elif status == "FAILED":
                success_weight -= weight * 0.8  # penalty

        if total_weight == 0:
            return 1.0

        return max(0, success_weight / total_weight)