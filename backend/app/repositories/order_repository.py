"""Order repository for database operations."""

from decimal import Decimal
from typing import Sequence

from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order, OrderSide, OrderStatus, OrderType


class OrderRepository:
    """Repository pattern for Order CRUD operations."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, order: Order) -> Order:
        """Create a new order."""
        self._session.add(order)
        await self._session.flush()
        await self._session.refresh(order)
        return order

    async def get_by_id(self, order_id: int) -> Order | None:
        """Get an order by ID."""
        result = await self._session.execute(
            select(Order).where(Order.id == order_id)
        )
        return result.scalar_one_or_none()

    async def get_open_buy_orders(self) -> Sequence[Order]:
        """Get all open buy orders sorted by highest price first, then earliest time."""
        result = await self._session.execute(
            select(Order)
            .where(
                Order.side == OrderSide.BUY,
                Order.status.in_([OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED]),
                Order.order_type == OrderType.LIMIT,
            )
            .order_by(Order.price.desc(), Order.created_at.asc())
        )
        return result.scalars().all()

    async def get_open_sell_orders(self) -> Sequence[Order]:
        """Get all open sell orders sorted by lowest price first, then earliest time."""
        result = await self._session.execute(
            select(Order)
            .where(
                Order.side == OrderSide.SELL,
                Order.status.in_([OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED]),
                Order.order_type == OrderType.LIMIT,
            )
            .order_by(Order.price.asc(), Order.created_at.asc())
        )
        return result.scalars().all()

    async def get_matching_sell_orders(self, max_price: Decimal) -> Sequence[Order]:
        """Get sell orders with price <= max_price, sorted by price-time priority."""
        result = await self._session.execute(
            select(Order)
            .where(
                Order.side == OrderSide.SELL,
                Order.status.in_([OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED]),
                Order.order_type == OrderType.LIMIT,
                Order.price <= max_price,
            )
            .order_by(Order.price.asc(), Order.created_at.asc())
        )
        return result.scalars().all()

    async def get_matching_buy_orders(self, min_price: Decimal) -> Sequence[Order]:
        """Get buy orders with price >= min_price, sorted by price-time priority."""
        result = await self._session.execute(
            select(Order)
            .where(
                Order.side == OrderSide.BUY,
                Order.status.in_([OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED]),
                Order.order_type == OrderType.LIMIT,
                Order.price >= min_price,
            )
            .order_by(Order.price.desc(), Order.created_at.asc())
        )
        return result.scalars().all()

    async def get_all_sell_orders_by_priority(self) -> Sequence[Order]:
        """Get all open sell orders sorted by price-time priority (for market orders)."""
        result = await self._session.execute(
            select(Order)
            .where(
                Order.side == OrderSide.SELL,
                Order.status.in_([OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED]),
                Order.order_type == OrderType.LIMIT,
            )
            .order_by(Order.price.asc(), Order.created_at.asc())
        )
        return result.scalars().all()

    async def get_all_buy_orders_by_priority(self) -> Sequence[Order]:
        """Get all open buy orders sorted by price-time priority (for market orders)."""
        result = await self._session.execute(
            select(Order)
            .where(
                Order.side == OrderSide.BUY,
                Order.status.in_([OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED]),
                Order.order_type == OrderType.LIMIT,
            )
            .order_by(Order.price.desc(), Order.created_at.asc())
        )
        return result.scalars().all()

    async def update_order(self, order: Order) -> Order:
        """Update an existing order."""
        await self._session.flush()
        await self._session.refresh(order)
        return order

    async def cancel_order(self, order_id: int) -> Order | None:
        """Cancel an open order."""
        order = await self.get_by_id(order_id)
        if order and order.status in (OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED):
            order.status = OrderStatus.CANCELLED
            await self._session.flush()
            await self._session.refresh(order)
            return order
        return None

    async def count_by_side(self, side: OrderSide) -> int:
        """Count total orders by side."""
        result = await self._session.execute(
            select(func.count(Order.id)).where(Order.side == side)
        )
        return result.scalar_one()

    async def count_open_by_side(self, side: OrderSide) -> int:
        """Count open orders by side."""
        result = await self._session.execute(
            select(func.count(Order.id)).where(
                Order.side == side,
                Order.status.in_([OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED]),
            )
        )
        return result.scalar_one()

    async def get_aggregated_buy_orders(self) -> list[dict]:
        """Get aggregated buy orders for order book display."""
        result = await self._session.execute(
            select(
                Order.price,
                func.sum(Order.remaining_quantity).label("quantity"),
                func.count(Order.id).label("order_count"),
            )
            .where(
                Order.side == OrderSide.BUY,
                Order.status.in_([OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED]),
                Order.order_type == OrderType.LIMIT,
            )
            .group_by(Order.price)
            .order_by(Order.price.desc())
        )
        return [
            {"price": row.price, "quantity": row.quantity, "order_count": row.order_count}
            for row in result.all()
        ]

    async def get_aggregated_sell_orders(self) -> list[dict]:
        """Get aggregated sell orders for order book display."""
        result = await self._session.execute(
            select(
                Order.price,
                func.sum(Order.remaining_quantity).label("quantity"),
                func.count(Order.id).label("order_count"),
            )
            .where(
                Order.side == OrderSide.SELL,
                Order.status.in_([OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED]),
                Order.order_type == OrderType.LIMIT,
            )
            .group_by(Order.price)
            .order_by(Order.price.asc())
        )
        return [
            {"price": row.price, "quantity": row.quantity, "order_count": row.order_count}
            for row in result.all()
        ]
