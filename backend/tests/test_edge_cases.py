"""Edge case tests for input validation and boundary conditions."""

import pytest
from httpx import AsyncClient


class TestInputValidation:
    """Test input validation edge cases."""

    @pytest.mark.asyncio
    async def test_negative_quantity(self, client: AsyncClient):
        response = await client.post("/api/orders", json={
            "side": "BUY", "price": 100, "quantity": -5
        })
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_zero_quantity(self, client: AsyncClient):
        response = await client.post("/api/orders", json={
            "side": "BUY", "price": 100, "quantity": 0
        })
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_negative_price(self, client: AsyncClient):
        response = await client.post("/api/orders", json={
            "side": "BUY", "price": -10, "quantity": 5
        })
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_zero_price_limit_order(self, client: AsyncClient):
        response = await client.post("/api/orders", json={
            "side": "BUY", "price": 0, "quantity": 5
        })
        assert response.status_code in (400, 422)

    @pytest.mark.asyncio
    async def test_invalid_side(self, client: AsyncClient):
        response = await client.post("/api/orders", json={
            "side": "INVALID", "price": 100, "quantity": 5
        })
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_empty_request(self, client: AsyncClient):
        response = await client.post("/api/orders", json={})
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_missing_side(self, client: AsyncClient):
        response = await client.post("/api/orders", json={
            "price": 100, "quantity": 5
        })
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_missing_quantity(self, client: AsyncClient):
        response = await client.post("/api/orders", json={
            "side": "BUY", "price": 100
        })
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_string_quantity(self, client: AsyncClient):
        response = await client.post("/api/orders", json={
            "side": "BUY", "price": 100, "quantity": "abc"
        })
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_decimal_precision(self, client: AsyncClient):
        """Decimal values should be handled properly."""
        response = await client.post("/api/orders", json={
            "side": "BUY", "price": 100.50, "quantity": 5.123456
        })
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_very_large_quantity(self, client: AsyncClient):
        """Excessively large quantities should be rejected."""
        response = await client.post("/api/orders", json={
            "side": "BUY", "price": 100, "quantity": 99999999999
        })
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_very_large_price(self, client: AsyncClient):
        """Excessively large prices should be rejected."""
        response = await client.post("/api/orders", json={
            "side": "BUY", "price": 99999999999, "quantity": 5
        })
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_invalid_order_type(self, client: AsyncClient):
        response = await client.post("/api/orders", json={
            "side": "BUY", "price": 100, "quantity": 5, "order_type": "STOP"
        })
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_case_insensitive_side(self, client: AsyncClient):
        """Side should be case insensitive."""
        response = await client.post("/api/orders", json={
            "side": "buy", "price": 100, "quantity": 5
        })
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_cancel_filled_order(self, client: AsyncClient):
        """Should not be able to cancel a filled order."""
        await client.post("/api/orders", json={"side": "SELL", "price": 95, "quantity": 5})
        response = await client.post("/api/orders", json={"side": "BUY", "price": 100, "quantity": 5})
        order_id = response.json()["order"]["id"]

        # Try to cancel the filled buy order
        cancel_response = await client.delete(f"/api/orders/{order_id}")
        assert cancel_response.status_code == 404  # Can't cancel filled order


class TestConcurrentScenarios:
    """Test scenarios involving multiple orders."""

    @pytest.mark.asyncio
    async def test_multiple_orders_same_price(self, client: AsyncClient):
        """Multiple orders at the same price should be time-priority ordered."""
        await client.post("/api/orders", json={"side": "SELL", "price": 100, "quantity": 3})
        await client.post("/api/orders", json={"side": "SELL", "price": 100, "quantity": 2})

        response = await client.post("/api/orders", json={"side": "BUY", "price": 100, "quantity": 4})
        data = response.json()

        # Should match first sell order completely (3), then partial second (1)
        assert len(data["trades"]) == 2
        assert float(data["trades"][0]["quantity"]) == 3
        assert float(data["trades"][1]["quantity"]) == 1

    @pytest.mark.asyncio
    async def test_order_persistence_after_match(self, client: AsyncClient):
        """Verify data consistency after matching."""
        await client.post("/api/orders", json={"side": "SELL", "price": 95, "quantity": 10})
        await client.post("/api/orders", json={"side": "BUY", "price": 100, "quantity": 3})

        # Verify orderbook still has remaining sell quantity
        response = await client.get("/api/orderbook")
        data = response.json()
        assert len(data["sell_orders"]) == 1
        assert float(data["sell_orders"][0]["quantity"]) == 7

    @pytest.mark.asyncio
    async def test_stats_consistency(self, client: AsyncClient):
        """Stats should reflect all orders and trades."""
        await client.post("/api/orders", json={"side": "SELL", "price": 95, "quantity": 5})
        await client.post("/api/orders", json={"side": "BUY", "price": 100, "quantity": 5})
        await client.post("/api/orders", json={"side": "BUY", "price": 90, "quantity": 3})

        response = await client.get("/api/stats")
        data = response.json()

        assert data["total_buy_orders"] == 2
        assert data["total_sell_orders"] == 1
        assert data["total_trades"] == 1
        assert data["open_buy_orders"] == 1  # The 90 buy is still open
