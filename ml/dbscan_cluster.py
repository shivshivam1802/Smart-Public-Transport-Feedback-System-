import csv
from typing import Any, Dict, List

import numpy as np
from sklearn.cluster import DBSCAN

def run_dbscan(csv_path):
    """
    Run DBSCAN on a CSV file that has `latitude` and `longitude` columns.
    Returns rows as dicts with an extra `cluster` field.
    """
    rows: List[Dict[str, Any]] = []
    coords: List[List[float]] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            lat = float(r["latitude"])
            lon = float(r["longitude"])
            rows.append(r)
            coords.append([lat, lon])

    if not coords:
        return []

    labels = DBSCAN(eps=0.01, min_samples=2).fit_predict(np.asarray(coords))
    for r, label in zip(rows, labels.tolist()):
        r["cluster"] = int(label)
    return rows


def run_dbscan_on_records(records):
    """
    Run DBSCAN on (latitude, longitude). records: list of objects with .latitude, .longitude.
    Returns list of cluster ids (same order); -1 = noise.
    """
    if not records:
        return []
    coords = np.asarray([[r.latitude, r.longitude] for r in records], dtype=float)
    labels = DBSCAN(eps=0.01, min_samples=2).fit_predict(coords)
    return labels.tolist()
