# backend/planning/cluster_utils.py

import numpy as np


def compute_cluster_centroids(reports):
    clusters = {}

    for r in reports:
        cid = r.get("cluster_id")
        if cid == -1:
            continue

        clusters.setdefault(cid, [])
        clusters[cid].append((r["lat"], r["lon"]))

    centroids = {}

    for cid, coords in clusters.items():
        arr = np.array(coords)
        centroid = arr.mean(axis=0)
        centroids[cid] = tuple(centroid)

    return centroids