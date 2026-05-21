"""Health check endpoint — confirms all services are running."""

from fastapi import APIRouter
import redis
import os
from sqlalchemy import text
from memory.database import AsyncSessionLocal

router = APIRouter()


@router.get("")
async def health_check():
    """Check status of all RAHI services."""
    status = {
        "rahi":     "online",
        "postgres": "unknown",
        "redis":    "unknown",
        "embeddings": "unknown",
    }

    # Check PostgreSQL
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        status["postgres"] = "healthy"
    except Exception as e:
        status["postgres"] = f"error: {str(e)}"

    # Check Redis
    try:
        r = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
        r.ping()
        status["redis"] = "healthy"
    except Exception as e:
        status["redis"] = f"error: {str(e)}"

    # Check Embeddings
    try:
        from memory.embeddings import get_model
        get_model()
        status["embeddings"] = "loaded"
    except Exception as e:
        status["embeddings"] = f"error: {str(e)}"

    # Overall status
    all_healthy = all(
        v in ("online", "healthy", "loaded")
        for v in status.values()
    )
    status["overall"] = "healthy" if all_healthy else "degraded"

    return status