"""
RAHI Basic API Key Authentication
===================================
Simple protection — without valid key, no access.
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import os

# Public endpoints — no auth needed
PUBLIC_PATHS = {"/", "/health", "/docs", "/openapi.json", "/redoc", "/favicon.ico"}


class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip auth for public paths
        if request.url.path in PUBLIC_PATHS:
            return await call_next(request)

        # Check API key
        api_key = request.headers.get("X-API-Key")
        expected = os.getenv("RAHI_API_KEY", "rahi-dev-key-2026")

        if api_key != expected:
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid or missing API key. Pass X-API-Key header."}
            )

        return await call_next(request)
