"""Order API routes."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.order import OrderCreate, OrderResponse, OrderBookResponse
from app.schemas.trade import TradeResponse
from app.services.order_service import OrderService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Orders"])


@router.post(
    "/orders",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Place a new order",
    description="Create a BUY or SELL order. The matching engine will automatically execute trades.",
)
async def create_order(
    order_data: OrderCreate,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Create a new order and return it with any executed trades."""
    try:
        service = OrderService(db)
        order, trades = await service.create_order(order_data)

        return {
            "order": OrderResponse.model_validate(order).model_dump(mode="json"),
            "trades": [
                TradeResponse.model_validate(t).model_dump(mode="json") for t in trades
            ],
            "message": f"Order created. {len(trades)} trade(s) executed.",
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating order: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get(
    "/orderbook",
    response_model=OrderBookResponse,
    summary="Get the order book",
    description="Returns aggregated buy and sell orders sorted by price-time priority.",
)
async def get_orderbook(
    db: AsyncSession = Depends(get_db),
) -> OrderBookResponse:
    """Get the current state of the order book."""
    service = OrderService(db)
    return await service.get_order_book()


@router.delete(
    "/orders/{order_id}",
    response_model=OrderResponse,
    summary="Cancel an order",
    description="Cancel an open or partially filled order.",
)
async def cancel_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
) -> OrderResponse:
    """Cancel an existing open order."""
    service = OrderService(db)
    order = await service.cancel_order(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order {order_id} not found or cannot be cancelled",
        )
    return OrderResponse.model_validate(order)


@router.get(
    "/orders/{order_id}",
    response_model=OrderResponse,
    summary="Get an order by ID",
    description="Retrieve a specific order by its ID.",
)
async def get_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
) -> OrderResponse:
    """Get a specific order by ID."""
    service = OrderService(db)
    order = await service.get_order(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order {order_id} not found",
        )
    return OrderResponse.model_validate(order)
