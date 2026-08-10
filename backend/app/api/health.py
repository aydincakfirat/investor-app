"""
Kubernetes health endpoints.

/api/health  — basic liveness (app process is alive)
/api/live    — liveness probe (same as health)
/api/ready   — readiness probe (checks DB connectivity)
"""
import time
import structlog
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.database.session import get_engine
from app.core.config import get_settings

logger = structlog.get_logger(__name__)
router = APIRouter(tags=["health"])

_start_time = time.time()


@router.get("/api/health", summary="Basic health check")
async def health() -> JSONResponse:
    settings = get_settings()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "healthy",
            "version": settings.app_version,
            "environment": settings.environment,
            "uptime_seconds": round(time.time() - _start_time, 1),
        },
    )


@router.get("/api/live", summary="Liveness probe")
async def liveness() -> JSONResponse:
    """
    Kubernetes liveness probe.
    Returns 200 if the process is running and the event loop is responsive.
    """
    return JSONResponse(status_code=status.HTTP_200_OK, content={"status": "alive"})


@router.get("/api/ready", summary="Readiness probe")
async def readiness() -> JSONResponse:
    """
    Kubernetes readiness probe.
    Returns 200 only when the database is reachable.
    Returns 503 if the database cannot be reached — Kubernetes will stop
    routing traffic to this pod until the probe passes again.
    """
    engine = get_engine()
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return JSONResponse(status_code=status.HTTP_200_OK, content={"status": "ready", "database": "ok"})
    except Exception as exc:
        logger.warning("readiness_probe_failed", error=str(exc))
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not_ready", "database": "unavailable"},
        )
