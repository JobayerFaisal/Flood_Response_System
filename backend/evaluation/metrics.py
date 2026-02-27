# backend/evaluation/metrics.py

def urgency_coverage(reports):
    total_high = sum(1 for r in reports if r["urgency"] >= 4)
    served = sum(1 for r in reports if r.get("served", False))
    if total_high == 0:
        return 1.0
    return served / total_high