"""
Pydantic-схемы для заказов.
Соответствует: SRS раздел 3.2 UC-3 (оформление заказа).
"""
from datetime import datetime
from pydantic import BaseModel, Field


class OrderItemCreate(BaseModel):
    """Позиция заказа при создании."""
    product_id: int
    quantity: float = Field(gt=0)


class OrderCreate(BaseModel):
    """Создание нового заказа."""
    pickup_point_id: int
    items: list[OrderItemCreate] = Field(min_length=1)
    payment_method: str = Field(default="card")


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str | None = None
    quantity: float
    price_at_order: float

    model_config = {"from_attributes": True}


class OrderResponse(BaseModel):
    id: int
    customer_id: int
    pickup_point_id: int
    order_date: datetime
    status: str
    total_amount: float
    payment_method: str
    payment_status: bool
    items: list[OrderItemResponse] = []

    model_config = {"from_attributes": True}


class OrderListResponse(BaseModel):
    items: list[OrderResponse]
    total: int
    page: int
    per_page: int


class OrderStatusUpdate(BaseModel):
    """Обновление статуса заказа (фермером, UC-6)."""
    status: str = Field(pattern="^(confirmed|ready|delivered|cancelled)$")
    reason: str | None = None  # Причина отклонения