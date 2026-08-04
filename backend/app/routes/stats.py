"""Stats API routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.stats import StatsResponse
from app.services.trade_service import TradeService

router = APIRouter(tags=["Statistics"])


@router.get(
    "/stats",
    response_model=StatsResponse,
    summary="Get system statistics",
    description="Returns aggregate system statistics including order counts and trade metrics.",
)
async def get_stats(
    db: AsyncSession = Depends(get_db),
) -> StatsResponse:
    """Get system statistics."""
    service = TradeService(db)
    return await service.get_stats()
