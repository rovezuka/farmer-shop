"""
Модель товара.
Соответствует: SRS раздел 4.2, таблица «Товары».
"""
import enum
from datetime import date

from sqlalchemy import (
    String, Text, Numeric, Float, Date, Enum, ForeignKey, CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class ProductStatus(str, enum.Enum):
    """Статусы товара (SRS раздел 4.2)."""
    ACTIVE = "active"           # В продаже
    PREORDER = "preorder"       # Предзаказ
    SEASON_ENDED = "season_ended"  # Сезон окончен


class ProductUnit(str, enum.Enum):
    """Единицы измерения."""
    KG = "кг"
    LITER = "л"
    PIECE = "шт"


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        CheckConstraint("price > 0", name="check_price_positive"),
        CheckConstraint("quantity >= 0", name="check_quantity_non_negative"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    farmer_id: Mapped[int] = mapped_column(
        ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[float] = mapped_column(
        Numeric(10, 2), nullable=False
    )
    unit: Mapped[ProductUnit] = mapped_column(
        Enum(ProductUnit), default=ProductUnit.KG
    )
    quantity: Mapped[float] = mapped_column(
        Numeric(10, 2), nullable=False, default=0
    )
    expiration_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[ProductStatus] = mapped_column(
        Enum(ProductStatus), default=ProductStatus.ACTIVE
    )
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[date] = mapped_column(Date, default=date.today)

    # Relationships
    farmer: Mapped["Farmer"] = relationship(back_populates="products")
    category: Mapped["Category"] = relationship(back_populates="products")
    order_items: Mapped[list["OrderItem"]] = relationship(back_populates="product")
    reviews: Mapped[list["Review"]] = relationship(back_populates="product")