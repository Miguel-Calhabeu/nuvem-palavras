"""Vercel entrypoint.

This file exposes the Flask `app` object so Vercel can run it as a Python Serverless Function.
"""

from server import app  # noqa: F401
