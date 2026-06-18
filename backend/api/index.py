"""Vercel Serverless Function entry point for CrazyMail backend.

Wraps the FastAPI app with Mangum so Vercel's Python runtime can handle it.
"""

from mangum import Mangum
from backend.main import app

handler = Mangum(app, lifespan="off")
