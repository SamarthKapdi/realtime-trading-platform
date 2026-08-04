"""Trade service for business logic."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import OrderSide
from app.models.trade import Trade
from app.repositories.order_repository import OrderRepository
from app.repositories.trade_repository import TradeRepository
from app.schemas.stats import StatsResponse


class TradeService:
    """Service layer for trade and statistics operations."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._trade_repo = TradeRepository(session)
        self._order_repo = OrderRepository(session)

    async def get_trades(self, limit: int = 100, offset: int = 0) -> list[Trade]:
        """Get recent trades."""
        return await self._trade_repo.get_all(limit=limit, offset=offset)

    async def get_stats(self) -> StatsResponse:
        """Get system statistics."""
        total_buy = await self._order_repo.count_by_side(OrderSide.BUY)
        total_sell = await self._order_repo.count_by_side(OrderSide.SELL)
        open_buy = await self._order_repo.count_open_by_side(OrderSide.BUY)
        open_sell = await self._order_repo.count_open_by_side(OrderSide.SELL)
        total_trades = await self._trade_repo.count()
        last_price = await self._trade_repo.get_last_trade_price()
        total_volume = await self._trade_repo.get_total_volume()

        return StatsResponse(
            total_buy_orders=total_buy,
            total_sell_orders=total_sell,
            total_trades=total_trades,
            open_buy_orders=open_buy,
            open_sell_orders=open_sell,
            last_trade_price=float(last_price) if last_price else None,
            total_volume=float(total_volume),
        )
