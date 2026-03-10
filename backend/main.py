"""
Smart Public Transport Feedback System – FastAPI backend.
- BERT sentiment: predict_sentiment() in services (or demo fallback).
- Multi-label classification: predict_issues() in services (sigmoid outputs).
- DBSCAN clustering: run_dbscan_on_records() in services; called by POST /admin/update-clusters.
"""
from pathlib import Path
from fastapi import FastAPI, Depends
from fastapi.responses import HTMLResponse, FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from collections import defaultdict, Counter

from .database import SessionLocal, engine
from . import models, schemas
from .services import predict_sentiment, predict_issues, run_dbscan_on_records
from .seed import seed_if_empty

# Create tables
models.Base.metadata.create_all(bind=engine)

# Auto-seed demo data (8–10 realistic complaints) if DB empty – for final-year demo
seed_if_empty()

app = FastAPI(
    title="Smart Public Transport Feedback System",
    description="Geo-tagged feedback with BERT sentiment, multi-label issue classification, and DBSCAN hotspot detection.",
)

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_clusters():
    """After seed, run DBSCAN so demo dashboard shows hotspots."""
    db = SessionLocal()
    try:
        records = db.query(models.Feedback).filter(
            models.Feedback.latitude.isnot(None),
            models.Feedback.longitude.isnot(None),
        ).all()
        if records:
            labels = run_dbscan_on_records(records)
            for r, label in zip(records, labels):
                r.cluster = int(label)
            db.commit()
    finally:
        db.close()


DEMO_DIR = Path(__file__).resolve().parent.parent / "demo"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


UI_HTML = """
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>Smart Transport Feedback</title></head>
<body>
<h1>Smart Public Transport Feedback System</h1>
<p><a href="/docs">API Docs (/docs)</a></p>
<p><a href="/api">API Info (/api)</a></p>
<p><a href="/demo/entry">Data Entry (jada data daalein)</a> | <a href="/demo">Demo</a></p>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def serve_ui_root():
    return UI_HTML


@app.get("/ui", response_class=HTMLResponse, include_in_schema=False)
def serve_ui():
    return UI_HTML


@app.get("/ui/", response_class=HTMLResponse, include_in_schema=False)
def serve_ui_slash():
    return UI_HTML


# ----- Demo routes (final-year presentation) -----
@app.get("/demo", response_class=HTMLResponse, include_in_schema=False)
def demo_landing():
    """Demo landing page – project explanation."""
    p = DEMO_DIR / "landing.html"
    if not p.exists():
        return HTMLResponse("<h1>Demo</h1><p><a href='/demo/dashboard'>Dashboard</a> | <a href='/demo/submit'>Submit</a></p>", status_code=200)
    return FileResponse(p, media_type="text/html")


@app.get("/demo/dashboard", response_class=HTMLResponse, include_in_schema=False)
def demo_dashboard():
    """Demo dashboard – analytics and hotspots (GET /analytics/summary, GET /analytics/clusters)."""
    p = DEMO_DIR / "dashboard.html"
    if not p.exists():
        return HTMLResponse("<h1>Dashboard</h1><p>Placeholder. Create demo/dashboard.html</p>", status_code=200)
    return FileResponse(p, media_type="text/html")


@app.get("/demo/submit", response_class=HTMLResponse, include_in_schema=False)
def demo_submit():
    """Demo feedback submission page (POST /feedback)."""
    p = DEMO_DIR / "submit.html"
    if not p.exists():
        return HTMLResponse("<h1>Submit</h1><p>Placeholder. Create demo/submit.html</p>", status_code=200)
    return FileResponse(p, media_type="text/html")


@app.get("/demo/entry", response_class=HTMLResponse, include_in_schema=False)
def demo_entry():
    """Single UI for data entry – form + list of all entries."""
    p = DEMO_DIR / "entry.html"
    if not p.exists():
        return HTMLResponse("<h1>Data Entry</h1><p>Create demo/entry.html</p>", status_code=200)
    return FileResponse(p, media_type="text/html")


@app.get("/api")
def api_info():
    """Project name and feature list."""
    return {
        "project": "Smart Public Transport Feedback System",
        "features": [
            "Contextual sentiment analysis – Fine-tuned BERT for positive/negative polarity.",
            "Multi-label issue detection – Overlapping issues: delay, overcrowding, cleanliness, staff, safety, infrastructure.",
            "Geo-spatial clustering – DBSCAN for high-density complaint areas (hotspots).",
            "Real-time pipeline – Submit feedback, preprocessing, sentiment + issues stored.",
            "Analytics API – Summary by sentiment/issue and cluster hotspots.",
        ],
    }


# BERT sentiment + multi-label classification run here (see services.py; demo fallback if BERT missing)
@app.post("/feedback", response_model=schemas.FeedbackResponse)
def submit_feedback(feedback: schemas.FeedbackCreate, db: Session = Depends(get_db)):
    """Clean text, BERT sentiment, multi-label issues; store and return sentiment + issues."""
    sentiment = predict_sentiment(feedback.text)
    issues = predict_issues(feedback.text)
    issues_str = ",".join(issues) if issues else ""
    record = models.Feedback(
        text=feedback.text,
        latitude=feedback.latitude,
        longitude=feedback.longitude,
        sentiment=sentiment,
        issues=issues_str,
        cluster=-1,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return schemas.FeedbackResponse(
        id=record.id,
        message="Feedback submitted",
        sentiment=sentiment,
        issues=issues,
    )


@app.get("/feedback")
def list_feedback(db: Session = Depends(get_db)):
    """List all stored feedback."""
    rows = db.query(models.Feedback).order_by(models.Feedback.id.desc()).all()
    return [
        {
            "id": r.id,
            "text": r.text,
            "sentiment": r.sentiment,
            "issues": r.issues.split(",") if r.issues else [],
            "latitude": r.latitude,
            "longitude": r.longitude,
            "cluster": r.cluster,
        }
        for r in rows
    ]


# DBSCAN clustering runs here – updates cluster field for each feedback (noise = -1)
@app.post("/admin/update-clusters")
def update_clusters(db: Session = Depends(get_db)):
    """Run DBSCAN on all lat/lon; update cluster field (noise = -1)."""
    records = db.query(models.Feedback).filter(
        models.Feedback.latitude.isnot(None),
        models.Feedback.longitude.isnot(None),
    ).all()
    if not records:
        return {"message": "No geo-tagged feedback to cluster", "updated": 0}
    labels = run_dbscan_on_records(records)
    for r, label in zip(records, labels):
        r.cluster = int(label)
    db.commit()
    return {"message": "Clusters updated", "updated": len(records)}


@app.get("/analytics/summary", response_model=schemas.AnalyticsSummary)
def analytics_summary(db: Session = Depends(get_db)):
    """Counts by sentiment and by issue type."""
    total = db.query(models.Feedback).count()
    by_sentiment = (
        db.query(models.Feedback.sentiment, func.count(models.Feedback.id))
        .group_by(models.Feedback.sentiment)
        .all()
    )
    by_sentiment_dict = {str(s): c for s, c in by_sentiment if s}
    rows = db.query(models.Feedback.issues).all()
    issue_counts = {}
    for (issues_str,) in rows:
        if not issues_str:
            continue
        for issue in issues_str.split(","):
            issue = issue.strip()
            if issue:
                issue_counts[issue] = issue_counts.get(issue, 0) + 1
    return schemas.AnalyticsSummary(
        total_feedback=total,
        by_sentiment=by_sentiment_dict,
        by_issue=issue_counts,
    )


@app.get("/analytics/clusters")
def analytics_clusters(db: Session = Depends(get_db)):
    """Per cluster: cluster_id, complaint count, center lat/lon, top 3 issues."""
    rows = db.query(models.Feedback).filter(models.Feedback.cluster >= 0).all()
    clusters = defaultdict(list)
    for r in rows:
        clusters[r.cluster].append(r)
    result = []
    for cid, recs in sorted(clusters.items()):
        lats = [r.latitude for r in recs]
        lons = [r.longitude for r in recs]
        all_issues = []
        for r in recs:
            if r.issues:
                all_issues.extend(r.issues.split(","))
        top_issues = [k for k, _ in Counter(all_issues).most_common(3)]
        result.append({
            "cluster_id": cid,
            "count": len(recs),
            "center_lat": sum(lats) / len(lats),
            "center_lon": sum(lons) / len(lons),
            "top_issues": top_issues,
        })
    return result
