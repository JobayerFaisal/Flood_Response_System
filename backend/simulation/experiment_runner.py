# backend/simulation/experiment_runner.py

from typing import List, Dict, Any
from backend.simulation.scenario_engine import ScenarioEngine


def run_experiment(scenario_name: str, seeds: List[int], steps: int) -> Dict[str, Any]:

    results = []

    for seed in seeds:
        engine = ScenarioEngine()

        result = engine.execute_scenario(   # ✅ FIXED
            scenario_name=scenario_name,
            seed=seed,
            steps=steps
        )

        results.append(result["final_metrics"])

    if not results:
        return {}

    aggregated = {}
    keys = results[0].keys()

    for key in keys:
        values = [r[key] for r in results if key in r]
        aggregated[f"experiment_avg_{key}"] = sum(values) / len(values)

    return {
        "scenario": scenario_name,
        "seeds": seeds,
        "steps": steps,
        "experiment_summary": aggregated
    }