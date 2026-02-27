# run_demo.py

import argparse
from backend.simulation.scenario_engine import ScenarioEngine


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", type=str, required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--steps", type=int, default=5)

    args = parser.parse_args()

    engine = ScenarioEngine()

    result = engine.execute_scenario(
        scenario_name=args.scenario,
        seed=args.seed,
        steps=args.steps
    )

    print("\n===== FINAL METRICS =====")
    for k, v in result["final_metrics"].items():
        print(f"{k}: {round(v, 4)}")


if __name__ == "__main__":
    main()