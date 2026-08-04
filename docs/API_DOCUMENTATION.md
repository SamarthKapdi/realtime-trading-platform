# API Documentation

## Base URL

```
http://localhost:8000/api
```

Interactive docs available at: `http://localhost:8000/docs` (Swagger) and `http://localhost:8000/redoc` (ReDoc)

---

## Endpoints

### 1. Place Order

**POST** `/api/orders`

Create a new BUY or SELL order. The matching engine automatically executes trades if compatible orders exist.

**Request Body:**

```json
{
  "side": "BUY",
  "price": 100.00,
  "quantity": 5.0,
  "order_type": "LIMIT"
}
```

| Field      | Type    | Required | Description                           |
|------------|---------|----------|---------------------------------------|
| side       | string  | Yes      | `BUY` or `SELL`                       |
| price      | number  | No*      | Order price. Required for LIMIT orders |
| quantity   | number  | Yes      | Order quantity (> 0)                  |
| order_type | string  | No       | `LIMIT` (default) or `MARKET`         |

*Market orders do not require a price.

**Response (201 Created):**

```json
{
  "order": {
    "id": 1,
    "side": "BUY",
    "order_type": "LIMIT",
    "price": "100.00",
    "quantity": "5.00000000",
    "remaining_quantity": "2.00000000",
    "status": "PARTIALLY_FILLED",
    "created_at": "2024-01-01T10:30:00Z"
  },
  "trades": [
    {
      "id": 1,
      "buy_order_id": 1,
      "sell_order_id": 2,
      "price": "95.00",
      "quantity": "3.00000000",
      "executed_at": "2024-01-01T10:30:00Z"
    }
  ],
  "message": "Order created. 1 trade(s) executed."
}
```

**Error Responses:**

| Status | Description           |
|--------|-----------------------|
| 400    | Invalid order data    |
| 422    | Validation error      |
| 500    | Internal server error |

---

### 2. Get Order Book

**GET** `/api/orderbook`

Returns the current order book with aggregated price levels.

**Response (200 OK):**

```json
{
  "buy_orders": [
    { "price": "100.00", "quantity": "15.00000000", "order_count": 3 },
    { "price": "99.50", "quantity": "8.00000000", "order_count": 2 }
  ],
  "sell_orders": [
    { "price": "101.00", "quantity": "5.00000000", "order_count": 1 },
    { "price": "102.50", "quantity": "10.00000000", "order_count": 4 }
  ]
}
```

Buy orders are sorted highest price first. Sell orders are sorted lowest price first.

---

### 3. Get Trade History

**GET** `/api/trades`

Returns completed trades ordered by most recent first.

**Query Parameters:**

| Param  | Type | Default | Description                |
|--------|------|---------|----------------------------|
| limit  | int  | 100     | Max trades to return (1-1000) |
| offset | int  | 0       | Pagination offset          |

**Response (200 OK):**

```json
[
  {
    "id": 1,
    "buy_order_id": 1,
    "sell_order_id": 2,
    "price": "95.00",
    "quantity": "3.00000000",
    "executed_at": "2024-01-01T10:34:21Z"
  }
]
```

---

### 4. Get Statistics

**GET** `/api/stats`

Returns aggregate system statistics.

**Response (200 OK):**

```json
{
  "total_buy_orders": 42,
  "total_sell_orders": 38,
  "total_trades": 25,
  "open_buy_orders": 12,
  "open_sell_orders": 8,
  "last_trade_price": 97.50,
  "total_volume": 15230.00
}
```

---

### 5. Cancel Order

**DELETE** `/api/orders/{order_id}`

Cancel an open or partially filled order.

**Response (200 OK):**

```json
{
  "id": 1,
  "side": "BUY",
  "order_type": "LIMIT",
  "price": "100.00",
  "quantity": "5.00000000",
  "remaining_quantity": "5.00000000",
  "status": "CANCELLED",
  "created_at": "2024-01-01T10:30:00Z"
}
```

**Error Responses:**

| Status | Description                              |
|--------|------------------------------------------|
| 404    | Order not found or cannot be cancelled   |

---

### 6. Get Order by ID

**GET** `/api/orders/{order_id}`

Retrieve a specific order.

**Response (200 OK):**

```json
{
  "id": 1,
  "side": "BUY",
  "order_type": "LIMIT",
  "price": "100.00",
  "quantity": "5.00000000",
  "remaining_quantity": "2.00000000",
  "status": "PARTIALLY_FILLED",
  "created_at": "2024-01-01T10:30:00Z"
}
```

---

## WebSocket

**WS** `/ws`

Receive real-time updates for order book changes, new trades, and statistics updates.

**Messages from Server:**

```json
// Order book updated
{"type": "orderbook_update"}

// New trade executed
{"type": "trade", "data": {"id": 1, "price": "95.00", "quantity": "3.00000000", ...}}

// Statistics updated
{"type": "stats_update"}

// Heartbeat response
{"type": "pong"}
```

**Client Heartbeat:**

Send `ping` as text to keep connection alive. Server responds with `{"type": "pong"}`.

---

## Validation Rules

| Field    | Rule                                |
|----------|-------------------------------------|
| side     | Must be `BUY` or `SELL` (case-insensitive) |
| price    | Must be >= 0, max 1,000,000,000     |
| quantity | Must be > 0, max 1,000,000,000      |
| order_type| Must be `LIMIT` or `MARKET`        |
