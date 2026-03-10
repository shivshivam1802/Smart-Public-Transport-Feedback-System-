"""
Vercel serverless entrypoint.

Vercel automatically detects Python functions under the `api/` directory.
This file exposes the FastAPI app defined in `backend.main`.
"""

from backend.main import app  # noqa: F401

