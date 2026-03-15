"""
Модуль инициализации асинхронного подключения к PostgreSQL.
Используется SQLAlchemy 2.0 async API + asyncpg драйвер.
"""
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


# Асинхронный движок
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,          # SQL-логирование в режиме отладки
    pool_size=20,                  # Размер пула соединений
    max_overflow=10,               # Дополнительные соединения при пике
)

# Фабрика сессий
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,        # Объекты остаются доступны после коммита
)


class Base(DeclarativeBase):
    """Базовый класс для всех моделей."""
    pass


async def get_db() -> AsyncSession:
    """
    Dependency для FastAPI: создаёт сессию БД на время запроса.
    Используется как: db: AsyncSession = Depends(get_db)
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()