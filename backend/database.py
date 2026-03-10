import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


def _get_database_url() -> str:
    # Allow override (useful for deployments)
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        return env_url

    # Vercel serverless filesystem is read-only except /tmp
    if os.getenv("VERCEL") == "1":
        return "sqlite:////tmp/feedback.db"

    return "sqlite:///./feedback.db"


DATABASE_URL = _get_database_url()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()
