"""Initial migration - Create orders and trades tables.

Revision ID: 001_initial
Revises:
Create Date: 2024-01-01 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create orders table
    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "side",
            sa.Enum("BUY", "SELL", name="orderside"),
            nullable=False,
        ),
        sa.Column(
            "order_type",
            sa.Enum("LIMIT", "MARKET", name="ordertype"),
            nullable=False,
        ),
        sa.Column("price", sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column("quantity", sa.Numeric(precision=18, scale=8), nullable=False),
        sa.Column("remaining_quantity", sa.Numeric(precision=18, scale=8), nullable=False),
        sa.Column(
            "status",
            sa.Enum("OPEN", "PARTIALLY_FILLED", "FILLED", "CANCELLED", name="orderstatus"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_orders_side_status", "orders", ["side", "status"])
    op.create_index("ix_orders_side_price_created", "orders", ["side", "price", "created_at"])
    op.create_index("ix_orders_status", "orders", ["status"])

    # Create trades table
    op.create_table(
        "trades",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("buy_order_id", sa.Integer(), nullable=False),
        sa.Column("sell_order_id", sa.Integer(), nullable=False),
        sa.Column("price", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("quantity", sa.Numeric(precision=18, scale=8), nullable=False),
        sa.Column(
            "executed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["buy_order_id"], ["orders.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["sell_order_id"], ["orders.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_trades_executed_at", "trades", ["executed_at"])
    op.create_index("ix_trades_buy_order_id", "trades", ["buy_order_id"])
    op.create_index("ix_trades_sell_order_id", "trades", ["sell_order_id"])


def downgrade() -> None:
    op.drop_table("trades")
    op.drop_table("orders")
    op.execute("DROP TYPE IF EXISTS orderstatus")
    op.execute("DROP TYPE IF EXISTS ordertype")
    op.execute("DROP TYPE IF EXISTS orderside")
