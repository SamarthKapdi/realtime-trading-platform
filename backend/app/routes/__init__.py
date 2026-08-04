"""API routes package."""

from app.routes.orders import router as orders_router
from app.routes.trades import router as trades_router
from app.routes.stats import router as stats_router
from app.routes.websocket import router as websocket_router

__all__ = ["orders_router", "trades_router", "stats_router", "websocket_router"]
