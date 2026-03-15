"""
Конфигурация приложения через переменные окружения.
Используется Pydantic Settings для валидации.
"""
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Приложение
    APP_NAME: str = "Фермерская лавка API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # База данных
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "farmer_db"
    DB_USER: str = "farmer_user"
    DB_PASSWORD: str = "farmer_pass"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def DATABASE_URL_SYNC(self) -> str:
        """Синхронный URL для Alembic."""
        return (
            f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    # JWT
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()