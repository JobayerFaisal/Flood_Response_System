# backend/evaluation/ground_truth_evaluator.py

from shapely.geometry import shape


def compute_detection_iou(predicted_geojson, true_polygon):
    """
    Intersection over Union for flood detection.
    """

    predicted_poly = shape(predicted_geojson["features"][0]["geometry"])

    intersection = predicted_poly.intersection(true_polygon).area
    union = predicted_poly.union(true_polygon).area

    if union == 0:
        return 0.0

    return intersection / union


def compute_high_urgency_precision(clustered_reports, allocation_plan, true_high_urgency_ids):
    """
    Did we prioritize the correct urgent cases?
    """

    served_ids = []

    for r in clustered_reports:
        cid = r["cluster_id"]

        if cid in allocation_plan and allocation_plan[cid]["capacity_served"] > 0:
            served_ids.append(r["report_id"])

    true_positive = len(set(served_ids) & set(true_high_urgency_ids))

    if len(served_ids) == 0:
        return 0.0

    return true_positive / len(served_ids)


def compute_high_urgency_recall(clustered_reports, allocation_plan, true_high_urgency_ids):
    """
    Did we serve most of the true urgent cases?
    """

    served_ids = []

    for r in clustered_reports:
        cid = r["cluster_id"]

        if cid in allocation_plan and allocation_plan[cid]["capacity_served"] > 0:
            served_ids.append(r["report_id"])

    true_positive = len(set(served_ids) & set(true_high_urgency_ids))

    if len(true_high_urgency_ids) == 0:
        return 0.0

    return true_positive / len(true_high_urgency_ids)