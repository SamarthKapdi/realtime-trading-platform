"""Unit tests for the matching engine."""

import pytest
import pytest_asyncio
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order, OrderSide, OrderStatus, OrderType
from app.repositories.order_repository import OrderRepository
from app.repositories.trade_repository import TradeRepository
from app.services.matching_engine import MatchingEngine


class TestMatchingEngine:
    """Test suite for the matching engine."""

    @pytest.mark.asyncio
    async def test_no_match_when_buy_price_below_sell(self, db_session: AsyncSession):
        """No trade when buy price < sell price."""
        repo = OrderRepository(db_session)

        # Place a sell order at 100
        sell = Order(
            side=OrderSide.SELL, order_type=OrderType.LIMIT,
            price=Decimal("100"), quantity=Decimal("5"), remaining_quantity=Decimal("5"),
            status=OrderStatus.OPEN,
        )
        await repo.create(sell)
        await db_session.commit()

        # Place a buy order at 95 (below sell)
        buy = Order(
            side=OrderSide.BUY, order_type=OrderType.LIMIT,
            price=Decimal("95"), quantity=Decimal("3"), remaining_quantity=Decimal("3"),
            status=OrderStatus.OPEN,
        )
        await repo.create(buy)
        await db_session.flush()

        engine = MatchingEngine(db_session)
        trades = await engine.process_order(buy)

        assert len(trades) == 0
        assert buy.remaining_quantity == Decimal("3")
        assert buy.status == OrderStatus.OPEN

    @pytest.mark.asyncio
    async def test_complete_fill(self, db_session: AsyncSession):
        """Complete fill: equal quantities matched."""
        repo = OrderRepository(db_session)

        sell = Order(
            side=OrderSide.SELL, order_type=OrderType.LIMIT,
            price=Decimal("95"), quantity=Decimal("5"), remaining_quantity=Decimal("5"),
            status=OrderStatus.OPEN,
        )
        await repo.create(sell)
        await db_session.commit()

        buy = Order(
            side=OrderSide.BUY, order_type=OrderType.LIMIT,
            price=Decimal("100"), quantity=Decimal("5"), remaining_quantity=Decimal("5"),
            status=OrderStatus.OPEN,
        )
        await repo.create(buy)
        await db_session.flush()

        engine = MatchingEngine(db_session)
        trades = await engine.process_order(buy)

        assert len(trades) == 1
        assert trades[0].quantity == Decimal("5")
        assert trades[0].price == Decimal("95")  # Maker (sell) price
        assert buy.remaining_quantity == Decimal("0")
        assert buy.status == OrderStatus.FILLED
        assert sell.remaining_quantity == Decimal("0")
        assert sell.status == OrderStatus.FILLED

    @pytest.mark.asyncio
    async def test_partial_fill_buy_larger(self, db_session: AsyncSession):
        """Partial fill: buy quantity > sell quantity."""
        repo = OrderRepository(db_session)

        sell = Order(
            side=OrderSide.SELL, order_type=OrderType.LIMIT,
            price=Decimal("95"), quantity=Decimal("3"), remaining_quantity=Decimal("3"),
            status=OrderStatus.OPEN,
        )
        await repo.create(sell)
        await db_session.commit()

        buy = Order(
            side=OrderSide.BUY, order_type=OrderType.LIMIT,
            price=Decimal("100"), quantity=Decimal("10"), remaining_quantity=Decimal("10"),
            status=OrderStatus.OPEN,
        )
        await repo.create(buy)
        await db_session.flush()

        engine = MatchingEngine(db_session)
        trades = await engine.process_order(buy)

        assert len(trades) == 1
        assert trades[0].quantity == Decimal("3")
        assert trades[0].price == Decimal("95")
        assert buy.remaining_quantity == Decimal("7")
        assert buy.status == OrderStatus.PARTIALLY_FILLED
        assert sell.remaining_quantity == Decimal("0")
        assert sell.status == OrderStatus.FILLED

    @pytest.mark.asyncio
    async def test_partial_fill_sell_larger(self, db_session: AsyncSession):
        """Partial fill: sell quantity > buy quantity."""
        repo = OrderRepository(db_session)

        sell = Order(
            side=OrderSide.SELL, order_type=OrderType.LIMIT,
            price=Decimal("95"), quantity=Decimal("10"), remaining_quantity=Decimal("10"),
            status=OrderStatus.OPEN,
        )
        await repo.create(sell)
        await db_session.commit()

        buy = Order(
            side=OrderSide.BUY, order_type=OrderType.LIMIT,
            price=Decimal("100"), quantity=Decimal("3"), remaining_quantity=Decimal("3"),
            status=OrderStatus.OPEN,
        )
        await repo.create(buy)
        await db_session.flush()

        engine = MatchingEngine(db_session)
        trades = await engine.process_order(buy)

        assert len(trades) == 1
        assert trades[0].quantity == Decimal("3")
        assert buy.status == OrderStatus.FILLED
        assert sell.remaining_quantity == Decimal("7")
        assert sell.status == OrderStatus.PARTIALLY_FILLED

    @pytest.mark.asyncio
    async def test_multiple_fills(self, db_session: AsyncSession):
        """Large order matched against multiple smaller orders."""
        repo = OrderRepository(db_session)

        # Place multiple small sell orders
        for price in [Decimal("95"), Decimal("96"), Decimal("97")]:
            sell = Order(
                side=OrderSide.SELL, order_type=OrderType.LIMIT,
                price=price, quantity=Decimal("3"), remaining_quantity=Decimal("3"),
                status=OrderStatus.OPEN,
            )
            await repo.create(sell)
        await db_session.commit()

        # Place a large buy order that matches all sells
        buy = Order(
            side=OrderSide.BUY, order_type=OrderType.LIMIT,
            price=Decimal("100"), quantity=Decimal("9"), remaining_quantity=Decimal("9"),
            status=OrderStatus.OPEN,
        )
        await repo.create(buy)
        await db_session.flush()

        engine = MatchingEngine(db_session)
        trades = await engine.process_order(buy)

        assert len(trades) == 3
        assert trades[0].price == Decimal("95")  # Lowest price first
        assert trades[1].price == Decimal("96")
        assert trades[2].price == Decimal("97")
        assert buy.remaining_quantity == Decimal("0")
        assert buy.status == OrderStatus.FILLED

    @pytest.mark.asyncio
    async def test_price_priority_sell(self, db_session: AsyncSession):
        """Sell orders matched lowest price first."""
        repo = OrderRepository(db_session)

        # Sell at 98, then 95 - should match 95 first
        sell_high = Order(
            side=OrderSide.SELL, order_type=OrderType.LIMIT,
            price=Decimal("98"), quantity=Decimal("5"), remaining_quantity=Decimal("5"),
            status=OrderStatus.OPEN,
        )
        sell_low = Order(
            side=OrderSide.SELL, order_type=OrderType.LIMIT,
            price=Decimal("95"), quantity=Decimal("5"), remaining_quantity=Decimal("5"),
            status=OrderStatus.OPEN,
        )
        await repo.create(sell_high)
        await repo.create(sell_low)
        await db_session.commit()

        buy = Order(
            side=OrderSide.BUY, order_type=OrderType.LIMIT,
            price=Decimal("100"), quantity=Decimal("5"), remaining_quantity=Decimal("5"),
            status=OrderStatus.OPEN,
        )
        await repo.create(buy)
        await db_session.flush()

        engine = MatchingEngine(db_session)
        trades = await engine.process_order(buy)

        assert len(trades) == 1
        assert trades[0].price == Decimal("95")  # Lowest sell matched first

    @pytest.mark.asyncio
    async def test_price_priority_buy(self, db_session: AsyncSession):
        """Buy orders matched highest price first."""
        repo = OrderRepository(db_session)

        buy_low = Order(
            side=OrderSide.BUY, order_type=OrderType.LIMIT,
            price=Decimal("95"), quantity=Decimal("5"), remaining_quantity=Decimal("5"),
            status=OrderStatus.OPEN,
        )
        buy_high = Order(
            side=OrderSide.BUY, order_type=OrderType.LIMIT,
            price=Decimal("100"), quantity=Decimal("5"), remaining_quantity=Decimal("5"),
            status=OrderStatus.OPEN,
        )
        await repo.create(buy_low)
        await repo.create(buy_high)
        await db_session.commit()

        sell = Order(
            side=OrderSide.SELL, order_type=OrderType.LIMIT,
            price=Decimal("90"), quantity=Decimal("5"), remaining_quantity=Decimal("5"),
            status=OrderStatus.OPEN,
        )
        await repo.create(sell)
        await db_session.flush()

        engine = MatchingEngine(db_session)
        trades = await engine.process_order(sell)

        assert len(trades) == 1
        assert trades[0].price == Decimal("100")  # Highest buy matched first

    @pytest.mark.asyncio
    async def test_exact_price_match(self, db_session: AsyncSession):
        """Trade when buy price == sell price."""
        repo = OrderRepository(db_session)

        sell = Order(
            side=OrderSide.SELL, order_type=OrderType.LIMIT,
            price=Decimal("100"), quantity=Decimal("5"), remaining_quantity=Decimal("5"),
            status=OrderStatus.OPEN,
        )
        await repo.create(sell)
        await db_session.commit()

        buy = Order(
            side=OrderSide.BUY, order_type=OrderType.LIMIT,
            price=Decimal("100"), quantity=Decimal("5"), remaining_quantity=Decimal("5"),
            status=OrderStatus.OPEN,
        )
        await repo.create(buy)
        await db_session.flush()

        engine = MatchingEngine(db_session)
        trades = await engine.process_order(buy)

        assert len(trades) == 1
        assert trades[0].price == Decimal("100")

    @pytest.mark.asyncio
    async def test_market_order_buy(self, db_session: AsyncSession):
        """Market buy order matches best available sells."""
        repo = OrderRepository(db_session)

        sell = Order(
            side=OrderSide.SELL, order_type=OrderType.LIMIT,
            price=Decimal("95"), quantity=Decimal("5"), remaining_quantity=Decimal("5"),
            status=OrderStatus.OPEN,
        )
        await repo.create(sell)
        await db_session.commit()

        buy = Order(
            side=OrderSide.BUY, order_type=OrderType.MARKET,
            price=None, quantity=Decimal("3"), remaining_quantity=Decimal("3"),
            status=OrderStatus.OPEN,
        )
        await repo.create(buy)
        await db_session.flush()

        engine = MatchingEngine(db_session)
        trades = await engine.process_order(buy)

        assert len(trades) == 1
        assert trades[0].quantity == Decimal("3")
        assert trades[0].price == Decimal("95")

    @pytest.mark.asyncio
    async def test_market_order_no_liquidity(self, db_session: AsyncSession):
        """Market order cancelled when no liquidity available."""
        repo = OrderRepository(db_session)

        buy = Order(
            side=OrderSide.BUY, order_type=OrderType.MARKET,
            price=None, quantity=Decimal("5"), remaining_quantity=Decimal("5"),
            status=OrderStatus.OPEN,
        )
        await repo.create(buy)
        await db_session.flush()

        engine = MatchingEngine(db_session)
        trades = await engine.process_order(buy)

        assert len(trades) == 0
        assert buy.status == OrderStatus.CANCELLED

    @pytest.mark.asyncio
    async def test_trade_records_correct_order_ids(self, db_session: AsyncSession):
        """Trade correctly records buy and sell order IDs."""
        repo = OrderRepository(db_session)

        sell = Order(
            side=OrderSide.SELL, order_type=OrderType.LIMIT,
            price=Decimal("95"), quantity=Decimal("5"), remaining_quantity=Decimal("5"),
            status=OrderStatus.OPEN,
        )
        await repo.create(sell)
        await db_session.commit()

        buy = Order(
            side=OrderSide.BUY, order_type=OrderType.LIMIT,
            price=Decimal("100"), quantity=Decimal("5"), remaining_quantity=Decimal("5"),
            status=OrderStatus.OPEN,
        )
        await repo.create(buy)
        await db_session.flush()

        engine = MatchingEngine(db_session)
        trades = await engine.process_order(buy)

        assert trades[0].buy_order_id == buy.id
        assert trades[0].sell_order_id == sell.id
