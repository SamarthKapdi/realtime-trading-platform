"""WebSocket connection manager for real-time updates."""

import json
import logging
from typing import Any

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections and broadcasts updates."""

    def __init__(self) -> None:
        self._connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        """Accept and register a new WebSocket connection."""
        await websocket.accept()
        self._connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self._connections)}")

    def disconnect(self, websocket: WebSocket) -> None:
        """Remove a WebSocket connection."""
        if websocket in self._connections:
            self._connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self._connections)}")

    async def broadcast(self, message: dict[str, Any]) -> None:
        """Broadcast a message to all connected clients."""
        disconnected: list[WebSocket] = []
        data = json.dumps(message, default=str)

        for connection in self._connections:
            try:
                await connection.send_text(data)
            except Exception:
                disconnected.append(connection)

        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn)

    async def broadcast_order_update(self) -> None:
        """Notify clients that order book has been updated."""
        await self.broadcast({"type": "orderbook_update"})

    async def broadcast_trade(self, trade_data: dict[str, Any]) -> None:
        """Broadcast a new trade to all clients."""
        await self.broadcast({"type": "trade", "data": trade_data})

    async def broadcast_stats_update(self) -> None:
        """Notify clients that stats have been updated."""
        await self.broadcast({"type": "stats_update"})

    @property
    def connection_count(self) -> int:
        """Get the current number of connected clients."""
        return len(self._connections)


# Global singleton instance
ws_manager = WebSocketManager()
