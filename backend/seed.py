"""
Auto-seed database with realistic transport complaints for demo.
Mixed sentiments, multiple issues, close-by geo coordinates (for DBSCAN).
"""
from .database import SessionLocal
from . import models


DEMO_FEEDBACK = [
    {"text": "Bus was 20 minutes late. Very frustrating.", "sentiment": "negative", "issues": "delay", "lat": 30.7333, "lon": 76.7794},
    {"text": "Overcrowded during rush hour. Could barely stand.", "sentiment": "negative", "issues": "overcrowding", "lat": 30.7340, "lon": 76.7800},
    {"text": "Seats were dirty and bus smelled bad.", "sentiment": "negative", "issues": "cleanliness", "lat": 30.7325, "lon": 76.7788},
    {"text": "Driver was rude when I asked about the route.", "sentiment": "negative", "issues": "staff", "lat": 30.7350, "lon": 76.7810},
    {"text": "Felt unsafe at night. No proper lighting at stop.", "sentiment": "negative", "issues": "safety,infrastructure", "lat": 30.7338, "lon": 76.7798},
    {"text": "Clean bus and on time today. Good service.", "sentiment": "positive", "issues": "cleanliness", "lat": 30.7342, "lon": 76.7792},
    {"text": "Delay and overcrowding both. Need more buses on this route.", "sentiment": "negative", "issues": "delay,overcrowding,infrastructure", "lat": 30.7330, "lon": 76.7790},
    {"text": "Conductor was helpful. Bus was a bit late though.", "sentiment": "positive", "issues": "delay,staff", "lat": 30.7345, "lon": 76.7805},
    {"text": "Broken seats and dirty floor. Staff did not care.", "sentiment": "negative", "issues": "cleanliness,staff,infrastructure", "lat": 30.7328, "lon": 76.7785},
    {"text": "Safe and comfortable journey. Well maintained bus.", "sentiment": "positive", "issues": "", "lat": 30.7335, "lon": 76.7796},
]


def seed_if_empty():
    """Seed 8–10 realistic complaints if database has no feedback (for demo)."""
    db = SessionLocal()
    try:
        if db.query(models.Feedback).count() > 0:
            return
        for row in DEMO_FEEDBACK:
            db.add(models.Feedback(
                text=row["text"],
                sentiment=row["sentiment"],
                issues=row["issues"],
                latitude=row["lat"],
                longitude=row["lon"],
                cluster=-1,
            ))
        db.commit()
    finally:
        db.close()
