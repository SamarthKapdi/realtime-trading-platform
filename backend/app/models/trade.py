"""Trade model definition."""

from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Index, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Trade(Base):
    """Trade model representing an executed trade between two orders."""

    __tablename__ = "trades"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    buy_order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), nullable=False
    )
    sell_order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), nullable=False
    )
    price: Mapped[Decimal] = mapped_column(
        Numeric(precision=18, scale=2), nullable=False
    )
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(precision=18, scale=8), nullable=False
    )
    executed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    buy_order = relationship("Order", foreign_keys=[buy_order_id], lazy="selectin")
    sell_order = relationship("Order", foreign_keys=[sell_order_id], lazy="selectin")

    __table_args__ = (
        Index("ix_trades_executed_at", "executed_at"),
        Index("ix_trades_buy_order_id", "buy_order_id"),
        Index("ix_trades_sell_order_id", "sell_order_id"),
    )

    def __repr__(self) -> str:
        return (
            f"<Trade(id={self.id}, buy={self.buy_order_id}, "
            f"sell={self.sell_order_id}, price={self.price}, "
            f"qty={self.quantity})>"
        )
