"""
Модели заказа и позиции заказа.
Соответствует: SRS раздел 4.2, таблицы «Заказы» и «Позиции заказа».
"""
import enum
from datetime import datetime

from sqlalchemy import (
    String, Numeric, Boolean, Enum, ForeignKey, DateTime, CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class OrderStatus(str, enum.Enum):
    """Статусы заказа (SRS раздел 4.2)."""
    NEW = "new"                    # Новый
    CONFIRMED = "confirmed"        # Подтверждён фермером
    READY = "ready"                # Готов к выдаче
    DELIVERED = "delivered"        # Выдан
    CANCELLED = "cancelled"        # Отменён


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id"), nullable=False
    )
    pickup_point_id: Mapped[int] = mapped_column(
        ForeignKey("pickup_points.id"), nullable=False
    )
    order_date: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus), default=OrderStatus.NEW
    )
    total_amount: Mapped[float] = mapped_column(
        Numeric(10, 2), nullable=False
    )
    payment_method: Mapped[str] = mapped_column(
        String(50), default="card"
    )
    payment_status: Mapped[bool] = mapped_column(
        Boolean, default=False
    )

    # Relationships
    customer: Mapped["Customer"] = relationship(back_populates="orders")
    pickup_point: Mapped["PickupPoint"] = relationship(back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )