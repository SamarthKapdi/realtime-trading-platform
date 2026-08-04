"""API integration tests."""

import pytest
from httpx import AsyncClient


class TestHealthEndpoints:
    """Test health check endpoints."""

    @pytest.mark.asyncio
    async def test_root_health(self, client: AsyncClient):
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_api_health(self, client: AsyncClient):
        response = await client.get("/api/health")
        assert response.status_code == 200


class TestOrderAPI:
    """Test order endpoints."""

    @pytest.mark.asyncio
    async def test_create_buy_order(self, client: AsyncClient):
        response = await client.post("/api/orders", json={
            "side": "BUY", "price": 100, "quantity": 5
        })
        assert response.status_code == 201
        data = response.json()
        assert data["order"]["side"] == "BUY"
        assert float(data["order"]["price"]) == 100
        assert float(data["order"]["quantity"]) == 5
        assert data["order"]["status"] == "OPEN"

    @pytest.mark.asyncio
    async def test_create_sell_order(self, client: AsyncClient):
        response = await client.post("/api/orders", json={
            "side": "SELL", "price": 95, "quantity": 3
        })
        assert response.status_code == 201
        data = response.json()
        assert data["order"]["side"] == "SELL"

    @pytest.mark.asyncio
    async def test_create_order_and_match(self, client: AsyncClient):
        """Test end-to-end order creation and matching."""
        # Place sell order
        await client.post("/api/orders", json={
            "side": "SELL", "price": 95, "quantity": 3
        })

        # Place matching buy order
        response = await client.post("/api/orders", json={
            "side": "BUY", "price": 100, "quantity": 5
        })
        data = response.json()

        assert len(data["trades"]) == 1
        assert float(data["trades"][0]["quantity"]) == 3
        assert float(data["trades"][0]["price"]) == 95
        assert data["order"]["status"] == "PARTIALLY_FILLED"

    @pytest.mark.asyncio
    async def test_create_market_order(self, client: AsyncClient):
        """Test market order creation."""
        # Place a sell limit order first
        await client.post("/api/orders", json={
            "side": "SELL", "price": 95, "quantity": 5
        })

        # Place a market buy order
        response = await client.post("/api/orders", json={
            "side": "BUY", "order_type": "MARKET", "quantity": 3
        })
        data = response.json()

        assert len(data["trades"]) == 1
        assert float(data["trades"][0]["quantity"]) == 3

    @pytest.mark.asyncio
    async def test_get_order_by_id(self, client: AsyncClient):
        response = await client.post("/api/orders", json={
            "side": "BUY", "price": 100, "quantity": 5
        })
        order_id = response.json()["order"]["id"]

        response = await client.get(f"/api/orders/{order_id}")
        assert response.status_code == 200
        assert response.json()["id"] == order_id

    @pytest.mark.asyncio
    async def test_get_nonexistent_order(self, client: AsyncClient):
        response = await client.get("/api/orders/99999")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_cancel_order(self, client: AsyncClient):
        response = await client.post("/api/orders", json={
            "side": "BUY", "price": 100, "quantity": 5
        })
        order_id = response.json()["order"]["id"]

        response = await client.delete(f"/api/orders/{order_id}")
        assert response.status_code == 200
        assert response.json()["status"] == "CANCELLED"

    @pytest.mark.asyncio
    async def test_cancel_nonexistent_order(self, client: AsyncClient):
        response = await client.delete("/api/orders/99999")
        assert response.status_code == 404


class TestOrderBookAPI:
    """Test order book endpoint."""

    @pytest.mark.asyncio
    async def test_empty_orderbook(self, client: AsyncClient):
        response = await client.get("/api/orderbook")
        assert response.status_code == 200
        data = response.json()
        assert data["buy_orders"] == []
        assert data["sell_orders"] == []

    @pytest.mark.asyncio
    async def test_orderbook_with_orders(self, client: AsyncClient):
        await client.post("/api/orders", json={"side": "BUY", "price": 100, "quantity": 5})
        await client.post("/api/orders", json={"side": "BUY", "price": 99, "quantity": 3})
        await client.post("/api/orders", json={"side": "SELL", "price": 105, "quantity": 2})

        response = await client.get("/api/orderbook")
        data = response.json()

        assert len(data["buy_orders"]) == 2
        assert len(data["sell_orders"]) == 1
        # Buy orders sorted highest first
        assert float(data["buy_orders"][0]["price"]) == 100
        assert float(data["buy_orders"][1]["price"]) == 99

    @pytest.mark.asyncio
    async def test_orderbook_aggregation(self, client: AsyncClient):
        """Multiple orders at same price level should be aggregated."""
        await client.post("/api/orders", json={"side": "BUY", "price": 100, "quantity": 5})
        await client.post("/api/orders", json={"side": "BUY", "price": 100, "quantity": 3})

        response = await client.get("/api/orderbook")
        data = response.json()

        assert len(data["buy_orders"]) == 1
        assert float(data["buy_orders"][0]["quantity"]) == 8
        assert data["buy_orders"][0]["order_count"] == 2


class TestTradesAPI:
    """Test trades endpoint."""

    @pytest.mark.asyncio
    async def test_empty_trades(self, client: AsyncClient):
        response = await client.get("/api/trades")
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_trades_after_match(self, client: AsyncClient):
        await client.post("/api/orders", json={"side": "SELL", "price": 95, "quantity": 3})
        await client.post("/api/orders", json={"side": "BUY", "price": 100, "quantity": 5})

        response = await client.get("/api/trades")
        data = response.json()

        assert len(data) == 1
        assert float(data[0]["price"]) == 95
        assert float(data[0]["quantity"]) == 3


class TestStatsAPI:
    """Test stats endpoint."""

    @pytest.mark.asyncio
    async def test_initial_stats(self, client: AsyncClient):
        response = await client.get("/api/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["total_buy_orders"] == 0
        assert data["total_sell_orders"] == 0
        assert data["total_trades"] == 0

    @pytest.mark.asyncio
    async def test_stats_after_orders(self, client: AsyncClient):
        await client.post("/api/orders", json={"side": "BUY", "price": 100, "quantity": 5})
        await client.post("/api/orders", json={"side": "SELL", "price": 95, "quantity": 3})

        response = await client.get("/api/stats")
        data = response.json()

        assert data["total_buy_orders"] == 1
        assert data["total_sell_orders"] == 1
        assert data["total_trades"] == 1
