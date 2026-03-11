# backend/memory/learning_engine.py

class LearningEngine:

    def __init__(self, performance_tracker):
        self.performance_tracker = performance_tracker

    def adjust_volunteer_score(self, volunteer_id: str, base_score: float) -> float:

        success_rate = self.performance_tracker.get_success_rate(volunteer_id)

        # Penalize repeated failures
        adjustment = success_rate * 10

        return base_score + adjustment