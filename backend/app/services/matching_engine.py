"""Matching engine implementing price-time priority order matching."""

import logging
from decimal import Decimal
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order, OrderSide, OrderStatus, OrderType
from app.models.trade import Trade
from app.repositories.order_repository import OrderRepository
from app.repositories.trade_repository import TradeRepository

logger = logging.getLogger(__name__)


class MatchingEngine:
    """
    Core matching engine implementing price-time priority.

    Matching Rules:
    - BUY orders: highest price first, then earliest timestamp
    - SELL orders: lowest price first, then earliest timestamp
    - A trade executes when BUY PRICE >= SELL PRICE
    - Trade executes at the resting order's price (maker price)
    - Supports partial fills, complete fills, and multiple fills
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._order_repo = OrderRepository(session)
        self._trade_repo = TradeRepository(session)

    async def process_order(self, order: Order) -> list[Trade]:
        """
        Process an incoming order against the order book.

        Returns a list of trades that were executed.
        """
        if order.order_type == OrderType.MARKET:
            return await self._process_market_order(order)
        return await self._process_limit_order(order)

    async def _process_limit_order(self, order: Order) -> list[Trade]:
        """Process a limit order, matching against compatible resting orders."""
        trades: list[Trade] = []

        if order.side == OrderSide.BUY:
            # Find sell orders with price <= buy price
            matching_orders = await self._order_repo.get_matching_sell_orders(order.price)
            trades = await self._match_orders(order, matching_orders)
        else:
            # Find buy orders with price >= sell price
            matching_orders = await self._order_repo.get_matching_buy_orders(order.price)
            trades = await self._match_orders(order, matching_orders)

        return trades

    async def _process_market_order(self, order: Order) -> list[Trade]:
        """Process a market order, matching against best available prices."""
        if order.side == OrderSide.BUY:
            # Match against all sell orders, lowest price first
            matching_orders = await self._order_repo.get_all_sell_orders_by_priority()
        else:
            # Match against all buy orders, highest price first
            matching_orders = await self._order_repo.get_all_buy_orders_by_priority()

        trades = await self._match_orders(order, matching_orders)

        # If market order couldn't be fully filled, cancel remaining
        if order.remaining_quantity > 0:
            order.status = OrderStatus.CANCELLED
            await self._order_repo.update_order(order)
            logger.info(
                f"Market order {order.id} partially filled. "
                f"Remaining {order.remaining_quantity} cancelled."
            )

        return trades

    async def _match_orders(
        self, incoming: Order, resting_orders: Sequence[Order]
    ) -> list[Trade]:
        """
        Match an incoming order against a sequence of resting orders.

        Implements the core matching loop with:
        - Partial fills (incoming order partially filled)
        - Complete fills (incoming order fully filled)
        - Multiple fills (incoming order matches multiple resting orders)
        """
        trades: list[Trade] = []

        for resting in resting_orders:
            if incoming.remaining_quantity <= 0:
                break

            # Determine trade quantity (minimum of both remaining quantities)
            trade_qty = min(incoming.remaining_quantity, resting.remaining_quantity)

            # Trade executes at the resting (maker) order's price
            trade_price = resting.price

            # Determine buy and sell order IDs
            if incoming.side == OrderSide.BUY:
                buy_order_id = incoming.id
                sell_order_id = resting.id
            else:
                buy_order_id = resting.id
                sell_order_id = incoming.id

            # Create trade record
            trade = Trade(
                buy_order_id=buy_order_id,
                sell_order_id=sell_order_id,
                price=trade_price,
                quantity=trade_qty,
            )
            trade = await self._trade_repo.create(trade)
            trades.append(trade)

            # Update quantities
            incoming.remaining_quantity -= trade_qty
            resting.remaining_quantity -= trade_qty

            # Update order statuses
            self._update_order_status(incoming)
            self._update_order_status(resting)

            # Persist updates
            await self._order_repo.update_order(incoming)
            await self._order_repo.update_order(resting)

            logger.info(
                f"Trade executed: {trade_qty} @ {trade_price} "
                f"(Order {incoming.id} <-> Order {resting.id})"
            )

        return trades

    @staticmethod
    def _update_order_status(order: Order) -> None:
        """Update order status based on remaining quantity."""
        if order.remaining_quantity <= 0:
            order.remaining_quantity = Decimal("0")
            order.status = OrderStatus.FILLED
        elif order.remaining_quantity < order.quantity:
            order.status = OrderStatus.PARTIALLY_FILLED
