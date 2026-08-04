# Design Decisions

## Database: PostgreSQL

**Why PostgreSQL over alternatives?**

| Factor           | PostgreSQL      | SQLite         | MongoDB         |
|------------------|-----------------|----------------|-----------------|
| ACID Compliance  | ✅ Full          | ✅ Limited      | ⚠️ Configurable  |
| Concurrent Writes| ✅ Excellent     | ❌ Single-writer| ✅ Good          |
| Decimal Precision| ✅ NUMERIC type  | ⚠️ REAL only    | ⚠️ Double only   |
| Indexing         | ✅ Advanced      | ✅ Basic        | ✅ Good          |
| Production Ready | ✅ Yes           | ❌ No           | ✅ Yes           |

**Decision**: PostgreSQL provides the ACID guarantees essential for a trading system where every transaction must be consistent. Its NUMERIC type prevents floating-point errors in price calculations, and its advanced indexing supports the composite queries needed by the matching engine.

**Tradeoff**: PostgreSQL requires more setup than SQLite, but the consistency guarantees are non-negotiable for financial systems.

---

## Backend: FastAPI

**Why FastAPI over Flask/Django/Express?**

- **Async-native**: Built on Starlette with first-class `async/await` support, critical for I/O-bound trading operations
- **Automatic validation**: Pydantic integration validates all request bodies at the framework level
- **Auto-generated docs**: OpenAPI/Swagger documentation comes free
- **WebSocket support**: Native WebSocket handling without additional libraries
- **Type safety**: Python type hints throughout reduce bugs

**Tradeoff**: Smaller ecosystem than Django, but the async performance and validation features are more important for this use case.

---

## Frontend: React + TypeScript + Vite

**Why this combination?**

- **React**: Component-based architecture maps naturally to exchange UI panels
- **TypeScript**: Catches API contract mismatches at compile time, especially important when types cross the API boundary
- **Vite**: Sub-second hot reload during development, optimized production builds
- **TailwindCSS**: Rapid UI development with consistent design system

**State Management Choice: TanStack React Query**

React Query was chosen over Redux/Zustand because:
1. The primary state is **server state** (order book, trades, stats), not client state
2. React Query handles caching, deduplication, and background refetching automatically
3. WebSocket messages trigger `invalidateQueries` for instant UI updates
4. No boilerplate reducers or stores needed

---

## Matching Algorithm

### Price-Time Priority (FIFO)

This is the standard matching algorithm used by real exchanges (NYSE, NASDAQ, CME).

**How it works:**
1. **Price priority**: Best price gets filled first (highest buy, lowest sell)
2. **Time priority**: At the same price, earlier orders get filled first (FIFO)
3. **Maker price execution**: Trade executes at the resting (maker) order's price, rewarding liquidity providers

**Why not other algorithms?**
- **Pro-rata**: Fairer for large institutional orders but more complex and not standard for equity exchanges
- **Random**: No real-world exchange uses this
- **LIFO**: Would discourage early order placement

### Partial Fill Handling

Orders can be in four states: `OPEN` → `PARTIALLY_FILLED` → `FILLED` / `CANCELLED`

When an incoming order matches against multiple resting orders:
1. Match against the best-priced resting order
2. Fill the minimum of (incoming remaining, resting remaining)
3. Update both orders' remaining quantities
4. Create a trade record
5. Repeat until incoming is filled or no more matches

### Market Orders

Market orders match against the best available prices without a price limit:
- BUY market orders sweep the sell side from lowest to highest price
- SELL market orders sweep the buy side from highest to lowest price
- Any unfilled quantity is **cancelled** (no resting market orders on the book)

---

## Data Structures

### Order Storage

Orders are stored in PostgreSQL with a composite index on `(side, price, created_at)`. This allows the matching engine to retrieve compatible orders in price-time priority order with a single indexed query.

**Alternative considered**: In-memory heaps (priority queues) for O(1) best-price access. This was deferred to keep the initial implementation simpler and persistent, but would be the first optimization for production scale.

### Trade Storage

Trades are stored as immutable records with foreign keys to both participating orders. The `executed_at` timestamp is server-generated for consistency.

### Order Book Aggregation

The order book API aggregates orders by price level using SQL `GROUP BY`, returning total quantity and order count per level. This is more efficient than sending individual orders and is the standard exchange API pattern.

---

## Scaling Considerations

### Current Design: 100,000 Active Orders

The current PostgreSQL-backed design can handle this with proper indexing:
- Composite index `(side, price, created_at)` covers the matching engine's primary query
- Status index allows efficient filtering of open orders
- Connection pooling (pool_size=20, max_overflow=10) handles concurrent requests

### Scaling to 10,000 Trades/Minute

1. **In-Memory Order Book**: Move from DB queries to an in-memory sorted data structure (e.g., `SortedDict` or red-black tree) for O(log n) matching
2. **Redis Cache**: Cache the order book snapshot, invalidate on changes
3. **Dedicated Matching Worker**: Separate the matching engine into its own process/service with a message queue (Redis Streams / Kafka)
4. **Database Partitioning**: Partition trades table by `executed_at` for efficient historical queries
5. **Read Replicas**: Route read queries (orderbook, trades, stats) to replicas

### Production Architecture

```
Load Balancer
     │
  ┌──┴──┐
  │ API  │ ── Redis Cache ── Order Book Snapshot
  │Nodes │
  └──┬───┘
     │ Message Queue (Redis Streams)
  ┌──┴──────┐
  │Matching  │ ── In-Memory Order Book (Sorted Heaps)
  │ Engine   │
  └──┬──────┘
     │
  ┌──┴──┐
  │ PG  │ ── Partitioned by date, Read Replicas
  └─────┘
```

---

## Key Tradeoffs

| Decision | Chosen | Alternative | Rationale |
|----------|--------|-------------|-----------|
| DB queries for matching | PostgreSQL indexed queries | In-memory heaps | Simpler, persistent, sufficient for demo scale |
| Synchronous matching | Match in same request | Background worker | Lower latency, simpler architecture |
| WebSocket broadcast | Broadcast all updates | Channel subscription | Simpler for single-asset exchange |
| Maker-price execution | Resting order's price | Midpoint/average | Industry standard, rewards liquidity |
| Order aggregation | SQL GROUP BY | Application-level | Fewer bytes transferred, DB optimized |
| Market order remainder | Cancel unfilled | Keep as limit at last price | Standard exchange behavior |
