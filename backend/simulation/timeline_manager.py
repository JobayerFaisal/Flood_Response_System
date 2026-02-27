# backend/simulation/timeline_manager.py

from typing import Dict, Any, List


class TimelineManager:
    def __init__(self):
        self.steps: List[Dict[str, Any]] = []

    def add_step(self, step_index: int, state: Dict[str, Any]):
        """
        Store full state snapshot for a timestep.
        """
        self.steps.append({
            "step": step_index,
            **state
        })

    def get_all_steps(self) -> List[Dict[str, Any]]:
        return self.steps

    def get_final_state(self) -> Dict[str, Any]:
        if not self.steps:
            return {}
        return self.steps[-1]

    def aggregate_metrics(self) -> Dict[str, float]:
        """
        Aggregate metrics across all steps.
        """
        if not self.steps:
            return {}

        metrics_list = [s["metrics"] for s in self.steps if "metrics" in s]

        if not metrics_list:
            return {}

        aggregated = {}

        keys = metrics_list[0].keys()

        for key in keys:
            values = [m[key] for m in metrics_list if key in m]
            aggregated[f"avg_{key}"] = sum(values) / len(values)

        return aggregated
    
    