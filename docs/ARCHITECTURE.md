# Architecture Document

## System Architecture

ByteVox Exchange follows a **layered architecture** with clear separation of concerns.

### Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         CLIENT                              │
│   ┌─────────────────────────────────────────────────────┐   │
│   │               React SPA (Vite + TS)                 │   │
│   │  ┌──────────┬──────────┬──────────┬───────────────┐ │   │
│   │  │OrderForm │OrderBook │ Trades   │  DepthChart   │ │   │
│   │  └────┬─────┴────┬─────┴────┬─────┴───────┬───────┘ │   │
│   │       └──────────┼──────────┼─────────────┘          │   │
│   │       ┌──────────┴──────────┴──────────────┐         │   │
│   │       │  React Query (Server State Cache)  │         │   │
│   │       └──────────┬──────────┬──────────────┘         │   │
│   │           HTTP   │          │  WebSocket             │   │
│   │         (Axios)  │          │  (useWebSocket)        │   │
│   └──────────────────┼──────────┼────────────────────────┘   │
└──────────────────────┼──────────┼────────────────────────────┘
                       │          │
┌──────────────────────┼──────────┼────────────────────────────┐
│                   API GATEWAY                                │
│   ┌──────────────────┼──────────┼────────────────────────┐   │
│   │           FastAPI Application                        │   │
│   │                                                      │   │
│   │  ┌─── Routes Layer ──────────────────────────────┐   │   │
│   │  │  POST /api/orders    GET /api/orderbook       │   │   │
│   │  │  GET  /api/trades    GET /api/stats           │   │   │
│   │  │  DELETE /api/orders/{id}   WS /ws             │   │   │
│   │  └────────────────────┬──────────────────────────┘   │   │
│   │                       │                              │   │
│   │  ┌─── Service Layer ──┴──────────────────────────┐   │   │
│   │  │  OrderService   TradeService                  │   │   │
│   │  │  MatchingEngine WebSocketManager              │   │   │
│   │  └────────────────────┬──────────────────────────┘   │   │
│   │                       │                              │   │
│   │  ┌─── Repository Layer ┴────────────────────────┐    │   │
│   │  │  OrderRepository    TradeRepository           │   │   │
│   │  └────────────────────┬──────────────────────────┘   │   │
│   └───────────────────────┼──────────────────────────────┘   │
└───────────────────────────┼──────────────────────────────────┘
                            │
┌───────────────────────────┼──────────────────────────────────┐
│                    DATA LAYER                                │
│   ┌───────────────────────┴──────────────────────────┐       │
│   │          PostgreSQL 16                           │       │
│   │  ┌──────────┐      ┌──────────┐                 │       │
│   │  │  orders  │──FK──│  trades  │                 │       │
│   │  └──────────┘      └──────────┘                 │       │
│   └──────────────────────────────────────────────────┘       │
└──────────────────────────────────────────────────────────────┘
```

---

## Sequence Diagram: Order Placement

```
User        Frontend       API           OrderService    MatchingEngine   Database
 │              │            │                │                │              │
 │  Submit      │            │                │                │              │
 │  Order  ────>│            │                │                │              │
 │              │ POST       │                │                │              │
 │              │ /orders ──>│                │                │              │
 │              │            │  create_order  │                │              │
 │              │            │ ──────────────>│                │              │
 │              │            │                │  INSERT order  │              │
 │              │            │                │ ──────────────────────────── >│
 │              │            │                │                │              │
 │              │            │                │ process_order  │              │
 │              │            │                │ ──────────────>│              │
 │              │            │                │                │ SELECT       │
 │              │            │                │                │ matching ── >│
 │              │            │                │                │    orders    │
 │              │            │                │                │< ────────── │
 │              │            │                │                │              │
 │              │            │                │                │ FOR EACH     │
 │              │            │                │                │ match:       │
 │              │            │                │                │ INSERT trade │
 │              │            │                │                │ ──────────> │
 │              │            │                │                │ UPDATE orders│
 │              │            │                │                │ ──────────> │
 │              │            │                │                │              │
 │              │            │                │ <── trades[] ──│              │
 │              │            │                │                │              │
 │              │            │                │ COMMIT         │              │
 │              │            │                │ ──────────────────────────── >│
 │              │            │                │                │              │
 │              │            │                │ broadcast WS   │              │
 │              │            │                │ (orderbook_update, trade,     │
 │              │            │                │  stats_update)  │              │
 │              │            │                │                │              │
 │              │            │ <── response ──│                │              │
 │              │ <── 201 ───│                │                │              │
 │              │            │                │                │              │
 │  WS ──────── ── orderbook_update ──────── ── ──────────── ──             │
 │  update      │            │                │                │              │
 │ <────────────│            │                │                │              │
```

---

## Request Flow

### REST API Flow

1. **Client** sends HTTP request → **FastAPI Route**
2. Route validates request body with **Pydantic schema**
3. Route creates **Service** instance with DB session (dependency injection)
4. Service uses **Repository** to interact with database
5. For orders: Service invokes **Matching Engine** within same transaction
6. Service commits transaction and broadcasts **WebSocket** updates
7. Route returns **JSON response** to client

### WebSocket Flow

1. Client opens WebSocket connection to `/ws`
2. **WebSocketManager** registers the connection
3. On any data change (order, trade, stats), Manager broadcasts to all clients
4. Client receives message and **invalidates React Query caches**
5. React Query auto-refetches the affected data
6. Heartbeat: client sends `ping` every 30s, server responds with `pong`

---

## Matching Engine Flow

```
                    Incoming Order
                         │
                    ┌────┴────┐
                    │ LIMIT?  │
                    └────┬────┘
                   yes/     \no
                  /           \
          ┌──────┴──┐    ┌────┴────┐
          │  LIMIT  │    │ MARKET  │
          │  Order  │    │  Order  │
          └────┬────┘    └────┬────┘
               │              │
        ┌──────┴──────┐  ┌────┴──────────┐
        │ Find orders │  │ Find ALL      │
        │ where       │  │ opposite side │
        │ BUY >= SELL │  │ orders by     │
        └──────┬──────┘  │ price-time    │
               │         └────┬──────────┘
               │              │
          ┌────┴──────────────┴────┐
          │    Match Loop          │
          │                        │
          │  while remaining > 0   │
          │  AND matches exist:    │
          │    qty = min(rem, match)│
          │    CREATE trade        │
          │    UPDATE quantities   │
          │    UPDATE statuses     │
          └────────────┬───────────┘
                       │
              ┌────────┴────────┐
              │ Market order    │
              │ unfilled?       │
              │ → CANCEL rest   │
              │                 │
              │ Limit order     │
              │ unfilled?       │
              │ → REST on book  │
              └─────────────────┘
```

---

## Database Design

### ER Diagram

```
┌──────────────────────────────┐       ┌──────────────────────────────┐
│           ORDERS             │       │           TRADES             │
├──────────────────────────────┤       ├──────────────────────────────┤
│ id          SERIAL PK        │       │ id            SERIAL PK     │
│ side        ENUM(BUY,SELL)   │       │ buy_order_id  INT FK ──────>│
│ order_type  ENUM(LIMIT,MKT)  │       │ sell_order_id INT FK ──────>│
│ price       NUMERIC(18,2)   │       │ price         NUMERIC(18,2) │
│ quantity    NUMERIC(18,8)   │       │ quantity      NUMERIC(18,8) │
│ remaining_q NUMERIC(18,8)   │       │ executed_at   TIMESTAMPTZ   │
│ status      ENUM(OPEN,PF,   │       └──────────────────────────────┘
│             FILLED,CANCEL)  │
│ created_at  TIMESTAMPTZ     │
└──────────────────────────────┘

Indexes:
  orders: ix_orders_side_status (side, status)
          ix_orders_side_price_created (side, price, created_at)
          ix_orders_status (status)
  trades: ix_trades_executed_at (executed_at)
          ix_trades_buy_order_id (buy_order_id)
          ix_trades_sell_order_id (sell_order_id)
```

### Design Rationale

- **NUMERIC types** for price/quantity to avoid floating-point precision errors
- **Composite indexes** on `(side, price, created_at)` to optimize the matching engine's primary query pattern
- **Status index** for efficient filtering of open orders
- **Foreign keys with CASCADE** to maintain referential integrity
- **TIMESTAMPTZ** for timezone-aware timestamps
