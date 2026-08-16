"""
Investment Intelligence Platform — Backend Entry Point

Phase 1: Health / readiness endpoints only.
Financial analysis, signals, and AI layers are added in later phases.
"""
import structlog
from contextlib import asynccontextmanager
from app.api.health import router as health_router
from app.api.markets import router as markets_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.logging import setup_logging
from app.api.health import router as health_router

# Initialise structured logging before anything else.
setup_logging()
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    Startup: validate config, warm up connection pool.
    Shutdown: dispose the engine gracefully.
    """
    settings = get_settings()
    logger.info(
        "startup",
        app=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
    )

    # Lazy-import to avoid circular imports; engine is cached.
    from app.database.session import get_engine
    engine = get_engine()
    # Connection pool warm-up — surfaces DB problems at startup rather than
    # on the first real request.
    try:
        from sqlalchemy import text
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("database_connected")
    except Exception as exc:
        # Log but do not crash — readiness probe will report not-ready until
        # the database becomes available.
        logger.warning("database_not_available_at_startup", error=str(exc))

    yield

    logger.info("shutdown")
    await engine.dispose()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    # ── CORS ──────────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routers ───────────────────────────────────────────────────────────────
    app.include_router(health_router)
    app.include_router(markets_router)

    # ── Root redirect ─────────────────────────────────────────────────────────
    @app.get("/", include_in_schema=False)
    async def root():
        return JSONResponse({"service": settings.app_name, "docs": "/api/docs"})

    return app


app = create_app()
