# Smart Public Transport Feedback System

Geo-tagged public transport feedback system aligned with the paper **“Smart Public Transport Feedback System Using NLP and Machine Learning”**.

It supports:
- **Sentiment analysis** (transformer-based / BERT where available)
- **Multi-label issue classification** (delay, overcrowding, cleanliness, staff, safety, infrastructure)
- **Hotspot detection** using **DBSCAN** geo-spatial clustering

## Demo (recommended)

Run the backend, then open:

| URL | Purpose |
|-----|---------|
| `http://127.0.0.1:8000/demo` | Demo landing (overview + links) |
| `http://127.0.0.1:8000/demo/dashboard` | Dashboard (summary + hotspots map) |
| `http://127.0.0.1:8000/demo/submit` | Submit feedback (see predicted sentiment + issues) |

## Quickstart (Windows / macOS / Linux)

From the project root:

```bash
pip install -r backend/requirements.txt
python -m uvicorn backend.main:app --reload
```

Then open:
- **App**: `http://127.0.0.1:8000/` (or `http://127.0.0.1:8000/ui`)
- **API docs (Swagger)**: `http://127.0.0.1:8000/docs`
- **API info (JSON)**: `http://127.0.0.1:8000/api`

## API overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/feedback` | Submit geo-tagged text; returns predicted sentiment and issues |
| GET | `/feedback` | List recent feedback (used by dashboard) |
| POST | `/admin/update-clusters` | Run DBSCAN on stored feedback and update cluster IDs |
| GET | `/analytics/summary` | Counts by sentiment and issue type |
| GET | `/analytics/clusters` | Hotspot list: cluster id, count, center lat/lon, top issues |

## How it works (data flow)

1. **Submit**: `POST /feedback` with `text`, `latitude`, `longitude` → preprocessing → sentiment + issues → stored.
2. **Cluster**: `POST /admin/update-clusters` runs DBSCAN on (lat, lon) and updates `cluster` (noise = `-1`).
3. **Visualize**: dashboard reads `GET /analytics/summary` + `GET /analytics/clusters`.

## Suggested viva / presentation flow

1. Open `GET /demo` and explain the goal (geo-tagged complaints + NLP + hotspot analytics).
2. Open `GET /demo/dashboard` and show totals, issue breakdown, and DBSCAN hotspots map.
3. Open `GET /demo/submit` and submit a sample complaint, e.g.:
   - Text: `Bus was late and very crowded. Seats were dirty.`
   - Lat/Lon example: `30.7333`, `76.7794`
4. Optionally open `GET /docs` and highlight the main endpoints.

## Notes

- **Seed data**: on first run, the database is auto-seeded so the dashboard isn’t empty.
- **Demo fallback**: if BERT/transformers aren’t installed or loading fails, the app falls back to a lightweight rule/keyword-based pipeline so demos don’t crash. Search for: `Demo fallback – replace with trained BERT`.

## Project structure

```
backend/    FastAPI app + API endpoints
frontend/   Static UI assets
demo/       Demo pages (landing, dashboard, submit)
ml/         Preprocessing + models + clustering
data/       Sample data
```

## Tech stack

- **Backend**: FastAPI + Uvicorn
- **ML/NLP**: transformers/BERT (when available), multi-label classifier, DBSCAN
- **Storage**: SQLite (local)

## Screenshots (optional)

Add screenshots in a folder like `assets/` and link them here:
- Dashboard: `assets/dashboard.png`
- Submit page: `assets/submit.png`
