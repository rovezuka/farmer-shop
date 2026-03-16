"""
Роутер точек выдачи заказов.
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.pickup_point import PickupPoint

router = APIRouter(prefix="/pickup-points", tags=["Точки выдачи"])


class PickupPointResponse(BaseModel):
    id: int
    name: str
    address: str
    working_hours: str | None

    model_config = {"from_attributes": True}


@router.get("", response_model=list[PickupPointResponse])
async def get_pickup_points(db: AsyncSession = Depends(get_db)):
    """Список активных точек выдачи."""
    result = await db.execute(
        select(PickupPoint)
        .where(PickupPoint.is_active == True)
        .order_by(PickupPoint.name)
    )
    return result.scalars().all()
