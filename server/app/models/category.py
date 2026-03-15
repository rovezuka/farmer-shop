"""
Модель категории товаров (иерархическая через parent_id).
Соответствует: SRS раздел 4.2, таблица «Категории».
"""
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id"), nullable=True
    )

    # Self-referential relationship для подкатегорий
    children: Mapped[list["Category"]] = relationship(
        back_populates="parent"
    )
    parent: Mapped["Category | None"] = relationship(
        back_populates="children", remote_side=[id]
    )
    products: Mapped[list["Product"]] = relationship(back_populates="category")