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
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Smart Transport Feedback</title>
  <style>
    :root{
      --bg1:#0b1220; --bg2:#0f1b33;
      --card:#0f203d; --card2:#101a30;
      --text:#e8eefc; --muted:#a9b7d0;
      --accent:#6ee7ff; --accent2:#8b5cf6;
      --border:rgba(255,255,255,.10);
      --shadow:0 18px 60px rgba(0,0,0,.35);
      --radius:18px;
    }
    *{box-sizing:border-box}
    body{
      margin:0;
      font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial, "Noto Sans", "Helvetica Neue", sans-serif;
      color:var(--text);
      background: radial-gradient(1200px 700px at 20% 10%, rgba(139,92,246,.35), transparent 55%),
                  radial-gradient(900px 600px at 90% 20%, rgba(110,231,255,.25), transparent 55%),
                  linear-gradient(160deg, var(--bg1), var(--bg2));
      min-height:100vh;
    }
    a{color:inherit; text-decoration:none}
    .wrap{max-width:980px; margin:0 auto; padding:36px 18px 56px}
    .hero{
      border:1px solid var(--border);
      background: linear-gradient(160deg, rgba(255,255,255,.06), rgba(255,255,255,.02));
      box-shadow: var(--shadow);
      border-radius: var(--radius);
      padding: 28px 22px;
      overflow:hidden;
      position:relative;
    }
    .badge{
      display:inline-flex; align-items:center; gap:8px;
      padding:8px 12px; border-radius:999px;
      border:1px solid var(--border);
      background: rgba(0,0,0,.18);
      color: var(--muted);
      font-size: 13px;
    }
    .dot{
      width:10px; height:10px; border-radius:999px;
      background: linear-gradient(135deg, var(--accent), var(--accent2));
      box-shadow: 0 0 0 4px rgba(110,231,255,.12);
    }
    h1{margin:14px 0 8px; font-size: 28px; line-height:1.15}
    p{margin:0; color:var(--muted); line-height:1.6}
    .grid{display:grid; gap:14px; margin-top:18px}
    @media (min-width: 860px){ .grid{grid-template-columns: 1.15fr .85fr} h1{font-size:34px} }
    .card{
      border:1px solid var(--border);
      background: rgba(16,26,48,.55);
      border-radius: var(--radius);
      padding: 18px;
    }
    .card h2{margin:0 0 6px; font-size:16px}
    .actions{display:flex; flex-wrap:wrap; gap:10px; margin-top:14px}
    .btn{
      display:inline-flex; align-items:center; justify-content:center; gap:10px;
      padding:12px 14px;
      border-radius: 14px;
      border:1px solid var(--border);
      background: rgba(0,0,0,.18);
      font-weight: 600;
      letter-spacing:.2px;
      transition: transform .08s ease, background .12s ease, border-color .12s ease;
    }
    .btn:hover{transform: translateY(-1px); background: rgba(255,255,255,.06); border-color: rgba(255,255,255,.18)}
    .btn.primary{
      background: linear-gradient(135deg, rgba(110,231,255,.20), rgba(139,92,246,.20));
      border-color: rgba(110,231,255,.25);
    }
    .kpi{display:grid; gap:10px; margin-top:12px}
    .kpi .item{
      padding:12px 12px; border-radius:14px;
      border:1px solid var(--border);
      background: rgba(0,0,0,.14);
    }
    .kpi .item b{display:block; font-size:13px}
    .kpi .item span{display:block; color:var(--muted); font-size:13px; margin-top:4px}
    footer{margin-top:16px; color:rgba(233,238,252,.55); font-size:12px}
    code{
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
      font-size: 12px;
      padding:2px 6px;
      border-radius:10px;
      border:1px solid var(--border);
      background: rgba(0,0,0,.18);
      color: rgba(232,238,252,.92);
    }
  </style>
</head>
<body>
  <main class="wrap">
    <section class="hero">
      <div class="badge"><span class="dot"></span> FastAPI • Geo-tagged feedback • Hotspot analytics</div>
      <h1>Smart Public Transport Feedback System</h1>
      <p>
        Submit transport feedback with latitude/longitude, view sentiment & issue categories, and detect complaint hotspots using DBSCAN.
      </p>
      <div class="actions" aria-label="Quick links">
        <a class="btn primary" href="/demo">Open Demo</a>
        <a class="btn" href="/demo/submit">Submit Feedback</a>
        <a class="btn" href="/demo/dashboard">Dashboard</a>
        <a class="btn" href="/docs">API Docs</a>
        <a class="btn" href="/api">API Info</a>
      </div>
      <footer>
        Tip: For data entry view, open <code>/demo/entry</code>. For analytics JSON, use <code>/analytics/summary</code> and <code>/analytics/clusters</code>.
      </footer>
    </section>

    <section class="grid">
      <div class="card">
        <h2>What you can do</h2>
        <p>Use the demo UI for viva/presentation, or call the API directly.</p>
        <div class="kpi">
          <div class="item">
            <b>Demo flow</b>
            <span><code>/demo</code> → <code>/demo/dashboard</code> → <code>/demo/submit</code></span>
          </div>
          <div class="item">
            <b>Submit feedback</b>
            <span>POST <code>/feedback</code> with <code>text</code>, <code>latitude</code>, <code>longitude</code></span>
          </div>
          <div class="item">
            <b>Refresh hotspots</b>
            <span>POST <code>/admin/update-clusters</code> (DBSCAN)</span>
          </div>
        </div>
      </div>

      <div class="card">
        <h2>Quick start</h2>
        <p>Run locally with:</p>
        <p style="margin-top:10px">
          <code>pip install -r backend/requirements.txt</code><br/>
          <code>python -m uvicorn backend.main:app --reload</code>
        </p>
        <p style="margin-top:12px">Then open <code>http://127.0.0.1:8000</code></p>
      </div>
    </section>
  </main>
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
