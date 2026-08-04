"""Order schemas for request/response validation."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class OrderCreate(BaseModel):
    """Schema for creating a new order."""

    side: str = Field(..., description="Order side: BUY or SELL")
    price: Optional[Decimal] = Field(
        None, description="Order price (required for LIMIT orders)", ge=0
    )
    quantity: Decimal = Field(
        ..., description="Order quantity", gt=0
    )
    order_type: str = Field(
        default="LIMIT", description="Order type: LIMIT or MARKET"
    )

    @field_validator("side")
    @classmethod
    def validate_side(cls, v: str) -> str:
        v = v.upper().strip()
        if v not in ("BUY", "SELL"):
            raise ValueError("Side must be BUY or SELL")
        return v

    @field_validator("order_type")
    @classmethod
    def validate_order_type(cls, v: str) -> str:
        v = v.upper().strip()
        if v not in ("LIMIT", "MARKET"):
            raise ValueError("Order type must be LIMIT or MARKET")
        return v

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Quantity must be greater than 0")
        if v > Decimal("1000000000"):
            raise ValueError("Quantity exceeds maximum allowed value")
        return v

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None:
            if v < 0:
                raise ValueError("Price cannot be negative")
            if v > Decimal("1000000000"):
                raise ValueError("Price exceeds maximum allowed value")
        return v

    model_config = {"json_schema_extra": {
        "examples": [
            {"side": "BUY", "price": 100, "quantity": 5},
            {"side": "SELL", "price": 95, "quantity": 3},
            {"side": "BUY", "order_type": "MARKET", "quantity": 5},
        ]
    }}


class OrderResponse(BaseModel):
    """Schema for order response."""

    id: int
    side: str
    order_type: str
    price: Optional[Decimal]
    quantity: Decimal
    remaining_quantity: Decimal
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class OrderBookEntry(BaseModel):
    """Single entry in the order book (aggregated by price level)."""

    price: Decimal
    quantity: Decimal
    order_count: int

    model_config = {"from_attributes": True}


class OrderBookResponse(BaseModel):
    """Complete order book response."""

    buy_orders: list[OrderBookEntry]
    sell_orders: list[OrderBookEntry]
