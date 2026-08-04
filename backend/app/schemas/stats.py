"""Statistics schemas for response validation."""

from pydantic import BaseModel


class StatsResponse(BaseModel):
    """Schema for system statistics response."""

    total_buy_orders: int
    total_sell_orders: int
    total_trades: int
    open_buy_orders: int
    open_sell_orders: int
    last_trade_price: float | None = None
    total_volume: float = 0.0
