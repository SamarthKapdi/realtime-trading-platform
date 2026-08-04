"""Trade repository for database operations."""

from decimal import Decimal

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.trade import Trade


class TradeRepository:
    """Repository pattern for Trade CRUD operations."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, trade: Trade) -> Trade:
        """Create a new trade record."""
        self._session.add(trade)
        await self._session.flush()
        await self._session.refresh(trade)
        return trade

    async def get_all(self, limit: int = 100, offset: int = 0) -> list[Trade]:
        """Get all trades ordered by most recent first."""
        result = await self._session.execute(
            select(Trade)
            .order_by(Trade.executed_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def get_by_id(self, trade_id: int) -> Trade | None:
        """Get a trade by ID."""
        result = await self._session.execute(
            select(Trade).where(Trade.id == trade_id)
        )
        return result.scalar_one_or_none()

    async def count(self) -> int:
        """Count total trades."""
        result = await self._session.execute(
            select(func.count(Trade.id))
        )
        return result.scalar_one()

    async def get_last_trade_price(self) -> Decimal | None:
        """Get the price of the most recent trade."""
        result = await self._session.execute(
            select(Trade.price)
            .order_by(Trade.executed_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_total_volume(self) -> Decimal:
        """Get total traded volume."""
        result = await self._session.execute(
            select(func.coalesce(func.sum(Trade.quantity * Trade.price), 0))
        )
        return result.scalar_one()
