"""
Модель пользователя системы.
Соответствует: SRS раздел 4.2, таблица «Пользователи».
"""
import enum
from datetime import date

from sqlalchemy import String, Enum, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

class UserRole(str, enum.Enum):
    """Роли пользователей (SRS раздел 4.2)."""
    CUSTOMER = "customer"       # Покупатель
    FARMER = "farmer"           # Фермер
    ADMIN = "admin"             # Организатор (Администратор)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), nullable=False
    )
    reg_date: Mapped[date] = mapped_column(
        Date, default=date.today, nullable=False
    )

    # Relationships
    customer: Mapped["Customer"] = relationship(
        back_populates="user", uselist=False
    )
    farmer: Mapped["Farmer"] = relationship(
        back_populates="user", uselist=False
    )
    notifications: Mapped[list["Notification"]] = relationship(
        back_populates="user"
    )

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"