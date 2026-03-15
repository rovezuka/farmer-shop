"""
Модель фермера (производителя).
Соответствует: SRS раздел 4.2, таблица «Фермеры».
"""
from sqlalchemy import String, Boolean, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Farmer(Base):
    __tablename__ = "farmers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    farm_name: Mapped[str] = mapped_column(String(150), nullable=False)
    farm_address: Mapped[str] = mapped_column(String(250), nullable=True)
    phone: Mapped[str] = mapped_column(String(12), nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    # Координаты фермы для геофильтрации (UC-2)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="farmer")
    products: Mapped[list["Product"]] = relationship(back_populates="farmer")