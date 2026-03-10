import pandas as pd
from sklearn.cluster import DBSCAN

def run_dbscan(csv_path):
    df = pd.read_csv(csv_path)
    coords = df[['latitude', 'longitude']]
    df['cluster'] = DBSCAN(eps=0.01, min_samples=2).fit_predict(coords)
    return df


def run_dbscan_on_records(records):
    """
    Run DBSCAN on (latitude, longitude). records: list of objects with .latitude, .longitude.
    Returns list of cluster ids (same order); -1 = noise.
    """
    if not records:
        return []
    df = pd.DataFrame([{"latitude": r.latitude, "longitude": r.longitude} for r in records])
    coords = df[["latitude", "longitude"]]
    labels = DBSCAN(eps=0.01, min_samples=2).fit_predict(coords)
    return labels.tolist()
