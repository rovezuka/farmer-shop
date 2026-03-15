"""
Pydantic-схемы для товаров.
Соответствует: SRS раздел 3.2 UC-5 (добавление товара).
"""
from datetime import date
from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    """Создание нового товара (фермером)."""
    name: str = Field(max_length=100)
    description: str | None = Field(None, max_length=1000)
    price: float = Field(gt=0)
    unit: str = Field(default="кг", pattern="^(кг|л|шт)$")
    quantity: float = Field(ge=0)
    category_id: int
    expiration_date: date | None = None
    image_url: str | None = None


class ProductUpdate(BaseModel):
    """Обновление товара."""
    name: str | None = None
    description: str | None = None
    price: float | None = Field(None, gt=0)
    quantity: float | None = Field(None, ge=0)
    category_id: int | None = None
    expiration_date: date | None = None
    status: str | None = None
    image_url: str | None = None


class ProductResponse(BaseModel):
    """Ответ с данными товара."""
    id: int
    name: str
    description: str | None
    price: float
    unit: str
    quantity: float
    category_id: int
    category_name: str | None = None
    farmer_id: int
    farmer_name: str | None = None
    expiration_date: date | None
    status: str
    image_url: str | None
    avg_rating: float | None = None
    distance_km: float | None = None  # Для геофильтрации (UC-2)

    model_config = {"from_attributes": True}


class ProductListResponse(BaseModel):
    """Список товаров с пагинацией."""
    items: list[ProductResponse]
    total: int
    page: int
    per_page: int