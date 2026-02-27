# backend/planning/sitrep_generator.py

from datetime import datetime


def generate_sitrep(
    event,
    clustered_reports,
    allocation_plan,
    cluster_demand,
    metrics,
    boat_count
):
    boats_deployed = sum(
        alloc["boats_assigned"]
        for alloc in allocation_plan.values()
    )

    total_reports = len(clustered_reports)
    clusters_detected = len([
        cid for cid in cluster_demand.keys()
    ])

    recommendations = []

    if metrics["coverage"] < 0.8:
        recommendations.append("Deploy additional rescue boats")

    if metrics["unmet_ratio"] > 0.2:
        recommendations.append("Request regional assistance")

    if event.severity >= 4:
        recommendations.append("Activate emergency shelters")

    sitrep = {
        "incident_id": event.event_id,
        "timestamp": datetime.utcnow().isoformat(),
        "situation_summary": (
            f"Flood severity {event.severity} "
            f"with {event.trend} trend. "
            f"{total_reports} distress reports received."
        ),
        "flood": {
            "severity": event.severity,
            "confidence": round(event.confidence, 2),
            "trend": event.trend,
            "area": round(event.area, 4)
        },
        "operational_status": {
            "clusters_detected": clusters_detected,
            "total_reports": total_reports,
            "boats_available": boat_count,
            "boats_deployed": boats_deployed
        },
        "response_metrics": {
            "coverage": round(metrics["coverage"], 2),
            "high_urgency_coverage": round(metrics["high_urgency_cov"], 2),
            "unmet_demand_ratio": round(metrics["unmet_ratio"], 2),
            "avg_response_time": round(metrics["avg_response_time"], 2)
        },
        "risks": event.hazards,
        "recommendations": recommendations
    }

    return sitrep