"""ByteVox Exchange - Main Application."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import init_db
from app.routes import orders_router, trades_router, stats_router, websocket_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[no-untyped-def]
    """Application lifespan: startup and shutdown."""
    logger.info("Starting ByteVox Exchange...")
    await init_db()
    logger.info("Database initialized.")
    yield
    logger.info("Shutting down ByteVox Exchange...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="A simplified exchange for the fictional asset BYTE. "
    "Supports limit and market orders with price-time priority matching.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(orders_router, prefix="/api")
app.include_router(trades_router, prefix="/api")
app.include_router(stats_router, prefix="/api")
app.include_router(websocket_router)


@app.get("/", tags=["Health"])
async def health_check() -> dict:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@app.get("/api/health", tags=["Health"])
async def api_health() -> dict:
    """API health check."""
    return {"status": "ok"}
