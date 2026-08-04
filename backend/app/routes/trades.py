"""Trade API routes."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.trade import TradeResponse
from app.services.trade_service import TradeService

router = APIRouter(tags=["Trades"])


@router.get(
    "/trades",
    response_model=list[TradeResponse],
    summary="Get trade history",
    description="Returns completed trades ordered by most recent first.",
)
async def get_trades(
    limit: int = Query(default=100, ge=1, le=1000, description="Maximum number of trades"),
    offset: int = Query(default=0, ge=0, description="Offset for pagination"),
    db: AsyncSession = Depends(get_db),
) -> list[TradeResponse]:
    """Get trade history with pagination."""
    service = TradeService(db)
    trades = await service.get_trades(limit=limit, offset=offset)
    return [TradeResponse.model_validate(t) for t in trades]
