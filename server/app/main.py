"""
Точка входа FastAPI приложения «Фермерская лавка».
Автоматическая документация: http://localhost:8000/docs (Swagger UI)
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.api import auth, products, orders, analytics

# Создание приложения
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API системы автоматизации продажи местных фермерских продуктов",
    docs_url="/docs",       # Swagger UI
    redoc_url="/redoc",     # ReDoc
)

# CORS (SRS раздел 5.4: безопасность коммуникаций)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
API_PREFIX = "/api/v1"
app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(products.router, prefix=API_PREFIX)
app.include_router(orders.router, prefix=API_PREFIX)
app.include_router(analytics.router, prefix=API_PREFIX)
# Добавить остальные роутеры по мере реализации:
# app.include_router(categories.router, prefix=API_PREFIX)
# app.include_router(pickup_points.router, prefix=API_PREFIX)
# app.include_router(reviews.router, prefix=API_PREFIX)
# app.include_router(notifications.router, prefix=API_PREFIX)
# app.include_router(admin.router, prefix=API_PREFIX)


@app.get("/", tags=["Главная"])
async def root():
    return {
        "message": "Фермерская лавка API",
        "docs": "/docs",
        "version": settings.APP_VERSION,
    }


@app.get("/health", tags=["Здоровье"])
async def health_check():
    return {"status": "ok"}