"""
Роутер товаров.
Соответствует: SRS раздел 3.1 (функции для покупателя — каталог),
              SRS раздел 3.2 UC-2 (геофильтрация), UC-5 (добавление товара).
"""
import math
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models import Product, ProductStatus, Category, Farmer, Review
from app.models.user import User
from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductResponse, ProductListResponse
)
from app.core.dependencies import get_current_farmer, get_current_user

router = APIRouter(prefix="/products", tags=["Товары"])


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Расчёт расстояния между двумя точками по формуле гаверсинуса (в км).
    Используется для геоперсонализации (SRS раздел 2.1 цель 2).
    """
    R = 6371  # Радиус Земли в км
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
            math.sin(dlat / 2) ** 2
            + math.cos(math.radians(lat1))
            * math.cos(math.radians(lat2))
            * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


@router.get("", response_model=ProductListResponse)
async def get_products(
        db: AsyncSession = Depends(get_db),
        page: int = Query(1, ge=1),
        per_page: int = Query(12, ge=1, le=100),
        category_id: int | None = None,
        search: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        sort_by: str = Query("name", pattern="^(name|price|distance|created_at)$"),
        # Параметры для геофильтрации (UC-2)
        user_lat: float | None = None,
        user_lon: float | None = None,
        max_distance_km: float | None = None,
):
    """
    Получение каталога товаров с фильтрацией (UC-2).

    Поддерживает:
    - Фильтрацию по категории, цене, расстоянию
    - Поиск по названию
    - Сортировку по имени, цене, расстоянию
    - Пагинацию
    """
    query = (
        select(Product)
        .options(
            selectinload(Product.category),
            selectinload(Product.farmer),
        )
        .where(Product.status == ProductStatus.ACTIVE)
        .where(Product.quantity > 0)
    )

    # Фильтры
    if category_id:
        query = query.where(Product.category_id == category_id)
    if search:
        query = query.where(Product.name.ilike(f"%{search}%"))
    if min_price is not None:
        query = query.where(Product.price >= min_price)
    if max_price is not None:
        query = query.where(Product.price <= max_price)

    # Подсчёт общего количества
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Сортировка (по умолчанию по имени; по расстоянию — на уровне Python)
    if sort_by == "price":
        query = query.order_by(Product.price)
    elif sort_by == "created_at":
        query = query.order_by(Product.created_at.desc())
    else:
        query = query.order_by(Product.name)

    # Пагинация
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)

    result = await db.execute(query)
    products = result.scalars().all()

    # Формирование ответа с расстоянием
    items = []
    for p in products:
        distance = None
        if user_lat and user_lon and p.farmer and p.farmer.latitude:
            distance = round(
                haversine(user_lat, user_lon, p.farmer.latitude, p.farmer.longitude),
                1
            )

        # Средний рейтинг (можно оптимизировать через подзапрос)
        rating_result = await db.execute(
            select(func.avg(Review.rating)).where(Review.product_id == p.id)
        )
        avg_rating = rating_result.scalar()

        items.append(ProductResponse(
            id=p.id,
            name=p.name,
            description=p.description,
            price=float(p.price),
            unit=p.unit.value if hasattr(p.unit, 'value') else str(p.unit),
            quantity=float(p.quantity),
            category_id=p.category_id,
            category_name=p.category.name if p.category else None,
            farmer_id=p.farmer_id,
            farmer_name=p.farmer.farm_name if p.farmer else None,
            expiration_date=p.expiration_date,
            status=p.status.value if hasattr(p.status, 'value') else str(p.status),
            image_url=p.image_url,
            avg_rating=round(float(avg_rating), 1) if avg_rating else None,
            distance_km=distance,
        ))

    # Сортировка по расстоянию (если запрошена)
    if sort_by == "distance" and user_lat and user_lon:
        items.sort(key=lambda x: x.distance_km if x.distance_km else float("inf"))

    # Фильтрация по максимальному расстоянию
    if max_distance_km and user_lat and user_lon:
        items = [i for i in items if i.distance_km and i.distance_km <= max_distance_km]
        total = len(items)

    return ProductListResponse(items=items, total=total, page=page, per_page=per_page)


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    """Получение детальной информации о товаре."""
    result = await db.execute(
        select(Product)
        .options(selectinload(Product.category), selectinload(Product.farmer))
        .where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(404, detail="Товар не найден")

    rating_result = await db.execute(
        select(func.avg(Review.rating)).where(Review.product_id == product.id)
    )
    avg_rating = rating_result.scalar()

    return ProductResponse(
        id=product.id, name=product.name,
        description=product.description,
        price=float(product.price),
        unit=product.unit.value if hasattr(product.unit, 'value') else str(product.unit),
        quantity=float(product.quantity),
        category_id=product.category_id,
        category_name=product.category.name if product.category else None,
        farmer_id=product.farmer_id,
        farmer_name=product.farmer.farm_name if product.farmer else None,
        expiration_date=product.expiration_date,
        status=product.status.value if hasattr(product.status, 'value') else str(product.status),
        image_url=product.image_url,
        avg_rating=round(float(avg_rating), 1) if avg_rating else None,
    )


@router.post("", response_model=ProductResponse, status_code=201)
async def create_product(
        data: ProductCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_farmer),
):
    """
    Добавление нового товара фермером (UC-5).
    Только для авторизованных фермеров.
    """
    # Получаем профиль фермера
    from app.models.farmer import Farmer
    result = await db.execute(
        select(Farmer).where(Farmer.user_id == current_user.id)
    )
    farmer = result.scalar_one_or_none()
    if not farmer:
        raise HTTPException(404, "Профиль фермера не найден")
    if not farmer.is_verified:
        raise HTTPException(403, "Фермер не верифицирован. Дождитесь проверки.")

    product = Product(
        farmer_id=farmer.id,
        category_id=data.category_id,
        name=data.name,
        description=data.description,
        price=data.price,
        unit=data.unit,
        quantity=data.quantity,
        expiration_date=data.expiration_date,
        image_url=data.image_url,
    )
    db.add(product)
    await db.commit()
    await db.refresh(product)

    return ProductResponse(
        id=product.id, name=product.name, description=product.description,
        price=float(product.price), unit=str(product.unit),
        quantity=float(product.quantity), category_id=product.category_id,
        farmer_id=product.farmer_id, expiration_date=product.expiration_date,
        status=str(product.status), image_url=product.image_url,
    )


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
        product_id: int,
        data: ProductUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_farmer),
):
    """Обновление товара (только владелец-фермер)."""
    from app.models.farmer import Farmer
    farmer_result = await db.execute(
        select(Farmer).where(Farmer.user_id == current_user.id)
    )
    farmer = farmer_result.scalar_one_or_none()

    result = await db.execute(
        select(Product).where(Product.id == product_id, Product.farmer_id == farmer.id)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(404, "Товар не найден или не принадлежит вам")

    # Обновление только переданных полей
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    await db.commit()
    await db.refresh(product)

    return ProductResponse(
        id=product.id, name=product.name, description=product.description,
        price=float(product.price), unit=str(product.unit),
        quantity=float(product.quantity), category_id=product.category_id,
        farmer_id=product.farmer_id, expiration_date=product.expiration_date,
        status=str(product.status), image_url=product.image_url,
    )


@router.delete("/{product_id}", status_code=204)
async def delete_product(
        product_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_farmer),
):
    """Удаление товара фермером."""
    from app.models.farmer import Farmer
    farmer_result = await db.execute(
        select(Farmer).where(Farmer.user_id == current_user.id)
    )
    farmer = farmer_result.scalar_one_or_none()

    result = await db.execute(
        select(Product).where(Product.id == product_id, Product.farmer_id == farmer.id)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(404, "Товар не найден")

    await db.delete(product)
    await db.commit()