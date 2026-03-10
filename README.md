# Smart Public Transport Feedback System

Implementation aligned with the paper **"Smart Public Transport Feedback System Using NLP and Machine Learning"**: geo-tagged feedback with **transformer-based (BERT) sentiment analysis**, **multi-label issue classification**, and **DBSCAN geo-spatial clustering** for hotspot detection.

## Features

- **Contextual sentiment analysis** – Fine-tuned BERT for positive/negative polarity (replacing TF-IDF baselines).
- **Multi-label issue detection** – Overlapping issues: delay, overcrowding, cleanliness, staff, safety, infrastructure.
- **Geo-spatial clustering** – DBSCAN to find high-density complaint areas (hotspots) without fixed cluster count.
- **Real-time pipeline** – Submit feedback → preprocessing → sentiment + issues → stored; admin can run clustering for analytics.
- **Analytics API** – Summary by sentiment/issue and cluster hotspots for dashboards and alerts.

## Run the app

```bash
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload
```

- **Web UI:** http://127.0.0.1:8000/ or http://127.0.0.1:8000/ui
- **API docs:** http://127.0.0.1:8000/docs
- **API info (JSON):** http://127.0.0.1:8000/api

## API overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/feedback` | Submit geo-tagged text; returns predicted sentiment and issues |
| GET | `/feedback` | List recent feedback (for dashboard) |
| POST | `/admin/update-clusters` | Run DBSCAN on all feedback and update cluster IDs |
| GET | `/analytics/summary` | Counts by sentiment and by issue type |
| GET | `/analytics/clusters` | Hotspot list: cluster id, count, center lat/lon, top issues |

## Data flow

1. **Submit** – `POST /feedback` with `text`, `latitude`, `longitude`. Backend runs text cleaning, BERT sentiment, and multi-label classifier; saves result and returns sentiment + issues.
2. **Clustering** – Call `POST /admin/update-clusters` to run DBSCAN on stored (lat, lon) and update each record’s `cluster` (noise = -1).
3. **Dashboard** – Use `GET /analytics/summary` and `GET /analytics/clusters` for sentiment/issue breakdown and geographic hotspots.

---

## Final-Year Demo Instructions

### How to run

1. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
2. Start the server (from project root):
   ```bash
   uvicorn backend.main:app --reload
   ```
   Or: `python -m uvicorn backend.main:app --reload`
3. Open in browser: **http://127.0.0.1:8000** (or the port shown in the terminal).

### URLs to open

| URL | Purpose |
|-----|---------|
| **http://127.0.0.1:8000/demo** | Demo landing – project overview and links |
| **http://127.0.0.1:8000/demo/dashboard** | Analytics dashboard (total feedback, sentiment, issue counts, hotspots map) |
| **http://127.0.0.1:8000/demo/submit** | Submit a complaint; see predicted sentiment and issues |
| **http://127.0.0.1:8000/docs** | API documentation (Swagger) |
| **http://127.0.0.1:8000/api** | API info (project name and features) |

### Suggested demo flow for viva

1. **Introduction** – Open `/demo`. Explain: geo-tagged complaints, BERT for sentiment, multi-label for issue types, DBSCAN for hotspots.
2. **Dashboard** – Open `/demo/dashboard`. Show total feedback, sentiment distribution (positive vs negative), issue-wise bars, and the map with complaint hotspots (DBSCAN clusters). Mention that data is from `GET /analytics/summary` and `GET /analytics/clusters`.
3. **Submit** – Open `/demo/submit`. Enter a sample complaint (e.g. “Bus was late and very crowded. Seats were dirty.”) and valid latitude/longitude (e.g. 30.7333, 76.7794). Submit and show the returned **sentiment** (positive/negative) and **detected issues** (delay, overcrowding, cleanliness, etc.). Explain that the backend runs BERT sentiment and multi-label classification; if BERT is not installed, a rule-based demo fallback is used so the demo still runs.
4. **API** – Optionally open `/docs` and show `POST /feedback`, `GET /analytics/summary`, `GET /analytics/clusters`, and `POST /admin/update-clusters`. Explain that clustering is run on startup and after new feedback you can call update-clusters to refresh hotspots.

### Notes

- On first run, the database is auto-seeded with 8–10 realistic transport complaints (mixed sentiments, multiple issues, close-by coordinates) so the dashboard is not empty.
- If BERT/transformers are not installed or loading fails, the app uses a **demo fallback** (rule-based sentiment and keyword-based issues) so the demo does not crash during evaluation. Search the code for “Demo fallback – replace with trained BERT” to find these paths.
