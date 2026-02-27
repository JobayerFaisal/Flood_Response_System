# backend/planning/clustering.py

from sklearn.cluster import DBSCAN
import numpy as np


def cluster_reports(reports, eps=0.01, min_samples=3):
    """
    Cluster reports using DBSCAN.

    eps: geographic radius threshold
    min_samples: minimum reports to form a cluster
    """

    if not reports:
        return reports

    coords = np.array([[r["lat"], r["lon"]] for r in reports])

    if len(coords) < min_samples:
        for r in reports:
            r["cluster_id"] = -1
        return reports

    clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(coords)
    labels = clustering.labels_

    for report, label in zip(reports, labels):
        report["cluster_id"] = int(label)

    return reports