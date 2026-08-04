"""Trade schemas for response validation."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class TradeResponse(BaseModel):
    """Schema for trade response."""

    id: int
    buy_order_id: int
    sell_order_id: int
    price: Decimal
    quantity: Decimal
    executed_at: datetime

    model_config = {"from_attributes": True}
