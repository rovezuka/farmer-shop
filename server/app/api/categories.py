"""
Роутер категорий товаров.
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.category import Category

router = APIRouter(prefix="/categories", tags=["Категории"])


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: str | None
    parent_id: int | None

    model_config = {"from_attributes": True}


@router.get("", response_model=list[CategoryResponse])
async def get_categories(db: AsyncSession = Depends(get_db)):
    """Список всех категорий товаров."""
    result = await db.execute(select(Category).order_by(Category.name))
    return result.scalars().all()
