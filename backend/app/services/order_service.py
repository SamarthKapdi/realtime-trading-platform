"""Order service for business logic."""

import logging
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order, OrderSide, OrderStatus, OrderType
from app.models.trade import Trade
from app.repositories.order_repository import OrderRepository
from app.schemas.order import OrderCreate, OrderBookEntry, OrderBookResponse
from app.services.matching_engine import MatchingEngine
from app.services.websocket_manager import ws_manager

logger = logging.getLogger(__name__)


class OrderService:
    """Service layer for order operations."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._order_repo = OrderRepository(session)
        self._matching_engine = MatchingEngine(session)

    async def create_order(self, order_data: OrderCreate) -> tuple[Order, list[Trade]]:
        """
        Create a new order and attempt to match it.

        Returns the created order and any trades that were executed.
        """
        # Validate market order has no price
        order_type = OrderType(order_data.order_type)
        price = order_data.price

        if order_type == OrderType.MARKET:
            price = None
        elif price is None or price <= 0:
            raise ValueError("Limit orders require a positive price")

        # Create the order
        order = Order(
            side=OrderSide(order_data.side),
            order_type=order_type,
            price=price,
            quantity=order_data.quantity,
            remaining_quantity=order_data.quantity,
            status=OrderStatus.OPEN,
        )
        order = await self._order_repo.create(order)

        logger.info(f"Order created: {order}")

        # Run matching engine
        trades = await self._matching_engine.process_order(order)

        # Commit all changes atomically
        await self._session.commit()

        # Broadcast updates via WebSocket
        await ws_manager.broadcast_order_update()
        await ws_manager.broadcast_stats_update()

        for trade in trades:
            await ws_manager.broadcast_trade({
                "id": trade.id,
                "buy_order_id": trade.buy_order_id,
                "sell_order_id": trade.sell_order_id,
                "price": str(trade.price),
                "quantity": str(trade.quantity),
                "executed_at": trade.executed_at.isoformat() if trade.executed_at else None,
            })

        return order, trades

    async def get_order_book(self) -> OrderBookResponse:
        """Get the current order book with aggregated price levels."""
        buy_orders_raw = await self._order_repo.get_aggregated_buy_orders()
        sell_orders_raw = await self._order_repo.get_aggregated_sell_orders()

        buy_orders = [OrderBookEntry(**row) for row in buy_orders_raw]
        sell_orders = [OrderBookEntry(**row) for row in sell_orders_raw]

        return OrderBookResponse(buy_orders=buy_orders, sell_orders=sell_orders)

    async def cancel_order(self, order_id: int) -> Order | None:
        """Cancel an open order."""
        order = await self._order_repo.cancel_order(order_id)
        if order:
            await self._session.commit()
            await ws_manager.broadcast_order_update()
            await ws_manager.broadcast_stats_update()
            logger.info(f"Order {order_id} cancelled")
        return order

    async def get_order(self, order_id: int) -> Order | None:
        """Get a single order by ID."""
        return await self._order_repo.get_by_id(order_id)
