# backend/synthetic/scenario_runner.py

from shapely.geometry import Polygon
import numpy as np
from datetime import datetime, timedelta


def generate_reports(step, expansion, base_lat, base_lon, polygon):
    reports = []

    num_reports = 10 + step * 5

    centroid = polygon.centroid
    center_lat = centroid.y
    center_lon = centroid.x

    for i in range(num_reports):

        # 80% inside flood region
        if np.random.rand() < 0.8:
            lat = np.random.normal(center_lat, 0.02 + expansion / 2)
            lon = np.random.normal(center_lon, 0.02 + expansion / 2)
        else:
            lat = base_lat + np.random.uniform(-0.05, 0.2 + expansion)
            lon = base_lon + np.random.uniform(-0.05, 0.2 + expansion)

        urgency = np.random.randint(1, 6)

        # Increase medical critical cases as severity grows
        if step > 2 and np.random.rand() < 0.3:
            need_type = "medical"
            urgency = np.random.randint(4, 6)
        else:
            need_type = np.random.choice(
                ["rescue", "medical", "food", "water", "shelter"]
            )

        credibility = float(np.random.uniform(0.6 - 0.05 * step, 1.0))

        reports.append({
            "report_id": f"R{step}_{i}",
            "lat": float(lat),
            "lon": float(lon),
            "urgency": int(urgency),
            "need_type": need_type,
            "credibility": max(0.3, credibility)
        })

    return reports


def generate_true_blocked_roads(step):
    """
    Simulate ground truth blocked grid cells.
    """
    blocked = []
    for i in range(step):
        blocked.append((i + 1, i + 2))
    return blocked


def run_scenario(name: str, seed: int, steps: int = 5):
    if name != "S3":
        raise ValueError("Only S3 implemented for now")

    np.random.seed(seed)

    base_lat = 23.0
    base_lon = 90.0
    start_time = datetime.utcnow()

    timeline = []

    for step in range(steps):
        expansion = 0.01 * step

        # -----------------------------
        # TRUE Flood Polygon
        # -----------------------------
        true_polygon = Polygon([
            (base_lon, base_lat),
            (base_lon + 0.1 + expansion, base_lat),
            (base_lon + 0.1 + expansion, base_lat + 0.1 + expansion),
            (base_lon, base_lat + 0.1 + expansion)
        ])

        # -----------------------------
        # Predicted polygon (slightly noisy)
        # -----------------------------
        noise = np.random.uniform(-0.002, 0.002)
        predicted_polygon = Polygon([
            (base_lon, base_lat),
            (base_lon + 0.1 + expansion + noise, base_lat),
            (base_lon + 0.1 + expansion + noise, base_lat + 0.1 + expansion + noise),
            (base_lon, base_lat + 0.1 + expansion + noise)
        ])

        reports = generate_reports(step, expansion, base_lat, base_lon, true_polygon)

        # -----------------------------
        # True High Urgency Ground Truth
        # -----------------------------
        true_high_urgency_ids = [
            r["report_id"] for r in reports if r["urgency"] >= 4
        ]

        # -----------------------------
        # True Blocked Roads
        # -----------------------------
        true_blocked_roads = generate_true_blocked_roads(step)

        # Risk signals
        weather_score = min(1.0, 0.6 + 0.05 * step)
        social_score = min(1.0, 0.5 + 0.06 * step)
        satellite_score = min(1.0, 0.7 + 0.05 * step)

        ground_truth = {
            "true_flood_polygon": true_polygon,
            "true_high_urgency_reports": true_high_urgency_ids,
            "true_blocked_roads": true_blocked_roads,
            "true_total_demand": len(reports),
        }

        timeline.append({
            "step": step,
            "timestamp": start_time + timedelta(minutes=10 * step),
            "polygon": predicted_polygon,
            "true_polygon": true_polygon,
            "area": predicted_polygon.area,
            "weather_score": weather_score,
            "social_score": social_score,
            "satellite_score": satellite_score,
            "reports": reports,
            "ground_truth": ground_truth,
            "evidence_refs": {
                "weather_stations": [f"WS{step}"],
                "social_reports": [r["report_id"] for r in reports],
                "satellite_tiles": [f"SAT{step}"]
            }
        })

    return timeline