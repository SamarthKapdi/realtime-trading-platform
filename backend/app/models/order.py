"""Order model definition."""

import enum
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import DateTime, Enum, Index, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class OrderSide(str, enum.Enum):
    """Order side: BUY or SELL."""
    BUY = "BUY"
    SELL = "SELL"


class OrderStatus(str, enum.Enum):
    """Order status lifecycle."""
    OPEN = "OPEN"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"


class OrderType(str, enum.Enum):
    """Order type: LIMIT or MARKET."""
    LIMIT = "LIMIT"
    MARKET = "MARKET"


class Order(Base):
    """Order model representing a buy or sell order."""

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    side: Mapped[OrderSide] = mapped_column(Enum(OrderSide), nullable=False)
    order_type: Mapped[OrderType] = mapped_column(
        Enum(OrderType), nullable=False, default=OrderType.LIMIT
    )
    price: Mapped[Decimal] = mapped_column(
        Numeric(precision=18, scale=2), nullable=True
    )
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(precision=18, scale=8), nullable=False
    )
    remaining_quantity: Mapped[Decimal] = mapped_column(
        Numeric(precision=18, scale=8), nullable=False
    )
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus), nullable=False, default=OrderStatus.OPEN
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        Index("ix_orders_side_status", "side", "status"),
        Index("ix_orders_side_price_created", "side", "price", "created_at"),
        Index("ix_orders_status", "status"),
    )

    def __repr__(self) -> str:
        return (
            f"<Order(id={self.id}, side={self.side}, price={self.price}, "
            f"qty={self.quantity}, remaining={self.remaining_quantity}, "
            f"status={self.status})>"
        )
