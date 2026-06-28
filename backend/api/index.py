"""Vercel Serverless Function entry point for CrazyMail backend.

Wraps the FastAPI app with Mangum so Vercel's Python runtime can handle it.
Updated: 2026-06-24 - Fix RFC2047 decode + message detail
"""

from mangum import Mangum
from backend.main import app

handler = Mangum(app, lifespan="off")
