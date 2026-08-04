# ByteVox Exchange

A simplified exchange simulator for the fictional asset **BYTE**. Users can place buy and sell orders, which are automatically matched using a price-time priority matching engine. Built as a full-stack application with real-time WebSocket updates.

<div align="center">

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

</div>

---

## Overview

ByteVox Exchange is a simulation trading platform that demonstrates core exchange mechanics:

- **Order Submission**: Place BUY and SELL limit or market orders
- **Matching Engine**: Automatic price-time priority order matching
- **Order Book**: Real-time aggregated view of buy/sell depth
- **Trade History**: Complete record of executed trades
- **Depth Chart**: Visual representation of order book depth
- **Real-time Updates**: WebSocket-powered live data streaming
- **System Statistics**: Live tracking of orders, trades, and volume

> **Note**: This is a simulation. No authentication, wallets, payments, or cryptocurrency integrations are implemented.

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    Frontend (React + TS)                  │
│  ┌──────────┐ ┌────────────┐ ┌───────────┐ ┌──────────┐ │
│  │OrderForm │ │ OrderBook  │ │  Trades   │ │  Stats   │ │
│  └────┬─────┘ └─────┬──────┘ └─────┬─────┘ └────┬─────┘ │
│       │             │              │             │        │
│  ┌────┴─────────────┴──────────────┴─────────────┴──┐    │
│  │         React Query + WebSocket Hook             │    │
│  └───────────────────┬──────────────────────────────┘    │
└──────────────────────┼───────────────────────────────────┘
                       │ HTTP + WebSocket
┌──────────────────────┼───────────────────────────────────┐
│                 Backend (FastAPI)                         │
│  ┌───────────────────┴───────────────────────────────┐   │
│  │              API Routes (REST + WS)               │   │
│  ├───────────────────────────────────────────────────┤   │
│  │              Service Layer                        │   │
│  │  ┌──────────────┐  ┌────────────────────────────┐ │   │
│  │  │ OrderService │  │     Matching Engine        │ │   │
│  │  │ TradeService │  │  (Price-Time Priority)     │ │   │
│  │  └──────────────┘  └────────────────────────────┘ │   │
│  ├───────────────────────────────────────────────────┤   │
│  │           Repository Layer (SQLAlchemy)            │   │
│  └───────────────────┬───────────────────────────────┘   │
└──────────────────────┼───────────────────────────────────┘
                       │
              ┌────────┴────────┐
              │   PostgreSQL    │
              │  Orders|Trades  │
              └─────────────────┘
```

---

## Tech Stack

| Layer     | Technology                          |
|-----------|-------------------------------------|
| Frontend  | React 18, TypeScript, Vite, TailwindCSS |
| State     | TanStack React Query                |
| Charts    | Recharts                            |
| HTTP      | Axios                               |
| Realtime  | WebSocket (native)                  |
| Backend   | FastAPI (Python 3.12+)              |
| ORM       | SQLAlchemy 2.0 (async)              |
| Database  | PostgreSQL 16                       |
| Validation| Pydantic v2                         |
| Migration | Alembic                             |
| Testing   | pytest + pytest-asyncio, httpx      |
| Container | Docker + Docker Compose             |

---

## Folder Structure

```
bytevox-exchange/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── config.py            # Pydantic settings
│   │   ├── database.py          # SQLAlchemy engine & sessions
│   │   ├── models/
│   │   │   ├── order.py         # Order model
│   │   │   └── trade.py         # Trade model
│   │   ├── schemas/
│   │   │   ├── order.py         # Order schemas
│   │   │   ├── trade.py         # Trade schemas
│   │   │   └── stats.py         # Stats schema
│   │   ├── repositories/
│   │   │   ├── order_repository.py
│   │   │   └── trade_repository.py
│   │   ├── services/
│   │   │   ├── matching_engine.py    # Core matching logic
│   │   │   ├── order_service.py
│   │   │   ├── trade_service.py
│   │   │   └── websocket_manager.py
│   │   └── routes/
│   │       ├── orders.py        # Order endpoints
│   │       ├── trades.py        # Trade endpoints
│   │       ├── stats.py         # Stats endpoint
│   │       └── websocket.py     # WebSocket endpoint
│   ├── alembic/                 # Database migrations
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_matching_engine.py
│   │   ├── test_api.py
│   │   └── test_edge_cases.py
│   ├── requirements.txt
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── api/                 # Axios client & API functions
│   │   ├── components/          # React components
│   │   ├── hooks/               # Custom hooks (WebSocket, React Query)
│   │   ├── pages/               # Dashboard page
│   │   └── types/               # TypeScript interfaces
│   ├── vite.config.ts
│   └── package.json
├── docker/
│   ├── backend.Dockerfile
│   └── frontend.Dockerfile
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DESIGN_DECISIONS.md
│   └── API_DOCUMENTATION.md
├── docker-compose.yml
└── README.md
```

---

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+
- PostgreSQL 16 (or Docker)

### Option 1: Docker (Recommended)

```bash
# Start everything with one command
docker compose up --build
```

- Frontend: http://localhost
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 2: Local Development

**Backend:**

```bash
cd backend

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Set up database (ensure PostgreSQL is running)
# Update .env with your database URL

# Run server
uvicorn app.main:app --reload --port 8000
```

**Frontend:**

```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev
```

---

## Environment Variables

### Backend (`backend/.env`)

| Variable       | Default                                                              | Description          |
|----------------|----------------------------------------------------------------------|----------------------|
| DATABASE_URL   | postgresql+asyncpg://bytevox:bytevox@localhost:5432/bytevox_exchange | Database connection  |
| APP_NAME       | ByteVox Exchange                                                     | Application name     |
| APP_VERSION    | 1.0.0                                                                | API version          |
| DEBUG          | false                                                                | Debug mode           |
| HOST           | 0.0.0.0                                                             | Server host          |
| PORT           | 8000                                                                 | Server port          |
| CORS_ORIGINS   | ["http://localhost:5173"]                                            | Allowed CORS origins |

### Frontend (`frontend/.env`)

| Variable     | Default                      | Description       |
|--------------|------------------------------|--------------------|
| VITE_API_URL | http://localhost:8000/api    | Backend API URL    |
| VITE_WS_URL  | ws://localhost:8000/ws       | WebSocket URL      |

---

## API Documentation

### Endpoints

| Method | Endpoint          | Description              |
|--------|-------------------|--------------------------|
| POST   | /api/orders       | Place a new order        |
| GET    | /api/orderbook    | Get the order book       |
| GET    | /api/trades       | Get trade history        |
| GET    | /api/stats        | Get system statistics    |
| DELETE | /api/orders/{id}  | Cancel an order          |
| GET    | /api/orders/{id}  | Get order by ID          |
| WS     | /ws               | Real-time updates        |

See [API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md) for full details.

---

## Matching Algorithm

The matching engine implements **price-time priority** (FIFO):

1. **BUY orders** are sorted: highest price first, then earliest timestamp
2. **SELL orders** are sorted: lowest price first, then earliest timestamp
3. A trade executes when `BUY PRICE >= SELL PRICE`
4. Trade price is set to the **resting (maker) order's price**
5. Supports **partial fills**, **complete fills**, and **multiple fills**
6. **Market orders** match against best available prices

### Example

```
Order Book:
  SELL: 3 @ $95
  SELL: 5 @ $98

Incoming: BUY 10 @ $100

Result:
  Trade 1: 3 @ $95 (sell fully filled)
  Trade 2: 5 @ $98 (sell fully filled)
  Remaining: BUY 2 @ $100 (rests on book)
```

---

## Running Tests

### Backend

```bash
cd backend
pip install -r requirements.txt
pytest -v
```

### Frontend

```bash
cd frontend
npm test
```

---

## Future Improvements

- **Redis Integration**: Cache order book snapshots, reducing DB load
- **Priority Queue (Heap)**: In-memory order book using sorted heaps for O(1) best price access
- **Horizontal Scaling**: Separate matching engine as microservice, process sharding
- **Rate Limiting**: Throttle order submissions per IP/session
- **Order History API**: Paginated order history with filters
- **Stop Orders**: Stop-loss and stop-limit order types
- **WebSocket Channels**: Subscribe to specific data streams
- **Monitoring**: Prometheus metrics + Grafana dashboards
- **Load Testing**: Locust/k6 performance benchmarks

---

## License

This project was built as a technical assignment for ByteVox.
