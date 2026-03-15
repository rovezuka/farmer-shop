"""
Аналитика продаж для фермера (UC-7).
Соответствует: SRS раздел 3.2 UC-7, раздел 4.3.
"""
from datetime import date, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.db.database import get_db
from app.models import Order, OrderItem, Product, Farmer, OrderStatus
from app.models.user import User
from app.core.dependencies import get_current_farmer

router = APIRouter(prefix="/analytics", tags=["Аналитика"])


class SalesSummary(BaseModel):
    total_revenue: float
    total_orders: int
    total_items_sold: float
    top_products: list[dict]
    daily_revenue: list[dict]


@router.get("/sales", response_model=SalesSummary)
async def get_sales_analytics(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_farmer),
        period: str = Query("month", pattern="^(week|month|quarter)$"),
):
    """
    Аналитика продаж фермера (UC-7, SRS 4.3.1).

    Возвращает:
    - Общую выручку за период
    - Количество заказов
    - Топ-5 товаров
    - Динамику продаж по дням
    """
    farmer_result = await db.execute(
        select(Farmer).where(Farmer.user_id == current_user.id)
    )
    farmer = farmer_result.scalar_one()

    # Определяем период
    period_days = {"week": 7, "month": 30, "quarter": 90}
    start_date = date.today() - timedelta(days=period_days[period])

    # Базовый запрос: заказы с товарами этого фермера, только завершённые
    base_filter = (
        select(OrderItem)
        .join(Order)
        .join(Product)
        .where(Product.farmer_id == farmer.id)
        .where(Order.status.in_([OrderStatus.CONFIRMED, OrderStatus.READY, OrderStatus.DELIVERED]))
        .where(func.date(Order.order_date) >= start_date)
    )

    # Общая выручка
    revenue_result = await db.execute(
        select(func.sum(OrderItem.price_at_order * OrderItem.quantity))
        .select_from(OrderItem)
        .join(Order).join(Product)
        .where(Product.farmer_id == farmer.id)
        .where(Order.status.in_([OrderStatus.CONFIRMED, OrderStatus.READY, OrderStatus.DELIVERED]))
        .where(func.date(Order.order_date) >= start_date)
    )
    total_revenue = revenue_result.scalar() or 0

    # Количество заказов
    orders_result = await db.execute(
        select(func.count(func.distinct(Order.id)))
        .select_from(OrderItem)
        .join(Order).join(Product)
        .where(Product.farmer_id == farmer.id)
        .where(Order.status.in_([OrderStatus.CONFIRMED, OrderStatus.READY, OrderStatus.DELIVERED]))
        .where(func.date(Order.order_date) >= start_date)
    )
    total_orders = orders_result.scalar() or 0

    # Топ-5 товаров
    top_result = await db.execute(
        select(
            Product.name,
            func.sum(OrderItem.quantity).label("total_qty"),
            func.sum(OrderItem.price_at_order * OrderItem.quantity).label("total_revenue"),
        )
        .select_from(OrderItem)
        .join(Order).join(Product)
        .where(Product.farmer_id == farmer.id)
        .where(Order.status.in_([OrderStatus.CONFIRMED, OrderStatus.READY, OrderStatus.DELIVERED]))
        .where(func.date(Order.order_date) >= start_date)
        .group_by(Product.name)
        .order_by(func.sum(OrderItem.price_at_order * OrderItem.quantity).desc())
        .limit(5)
    )
    top_products = [
        {"name": row.name, "quantity_sold": float(row.total_qty), "revenue": float(row.total_revenue)}
        for row in top_result.all()
    ]

    # Динамика по дням
    daily_result = await db.execute(
        select(
            func.date(Order.order_date).label("day"),
            func.sum(OrderItem.price_at_order * OrderItem.quantity).label("revenue"),
        )
        .select_from(OrderItem)
        .join(Order).join(Product)
        .where(Product.farmer_id == farmer.id)
        .where(Order.status.in_([OrderStatus.CONFIRMED, OrderStatus.READY, OrderStatus.DELIVERED]))
        .where(func.date(Order.order_date) >= start_date)
        .group_by(func.date(Order.order_date))
        .order_by(func.date(Order.order_date))
    )
    daily_revenue = [
        {"date": str(row.day), "revenue": float(row.revenue)}
        for row in daily_result.all()
    ]

    return SalesSummary(
        total_revenue=float(total_revenue),
        total_orders=total_orders,
        total_items_sold=sum(p["quantity_sold"] for p in top_products),
        top_products=top_products,
        daily_revenue=daily_revenue,
    )