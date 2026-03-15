"""
Модель отзыва.
Соответствует: SRS раздел 4.2, таблица «Отзывы».
"""
from datetime import date

from sqlalchemy import Integer, Text, Date, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="check_rating_range"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id"), nullable=False
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"), nullable=False
    )
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    review_date: Mapped[date] = mapped_column(Date, default=date.today)

    # Relationships
    customer: Mapped["Customer"] = relationship(back_populates="reviews")
    product: Mapped["Product"] = relationship(back_populates="reviews")