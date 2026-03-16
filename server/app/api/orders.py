"""
Роутер заказов.
Соответствует: SRS раздел 3.2 UC-3 (оформление), UC-4 (отслеживание), UC-6 (подтверждение).
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models import (
    Order, OrderStatus, OrderItem, Product, Customer, Farmer
)
from app.models.user import User
from app.schemas.order import (
    OrderCreate, OrderResponse, OrderItemResponse, OrderListResponse, OrderStatusUpdate
)
from app.core.dependencies import (
    get_current_user, get_current_customer, get_current_farmer
)
from app.services.notification_service import send_notification

router = APIRouter(prefix="/orders", tags=["Заказы"])


@router.post("", response_model=OrderResponse, status_code=201)
async def create_order(
        data: OrderCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_customer),
):
    """
    Оформление заказа (UC-3).

    1. Проверяет наличие товаров
    2. Резервирует остатки (транзакция, SRS 4.4.2)
    3. Рассчитывает сумму
    4. Эмулирует оплату
    5. Создаёт заказ со статусом «Новый»
    """
    # Получаем профиль покупателя
    cust_result = await db.execute(
        select(Customer).where(Customer.user_id == current_user.id)
    )
    customer = cust_result.scalar_one_or_none()
    if not customer:
        raise HTTPException(400, "Профиль покупателя не найден")

    total_amount = 0.0
    order_items = []

    for item_data in data.items:
        # Получаем товар с блокировкой строки (FOR UPDATE) для транзакционности
        product_result = await db.execute(
            select(Product)
            .where(Product.id == item_data.product_id)
            .with_for_update()
        )
        product = product_result.scalar_one_or_none()

        if not product:
            raise HTTPException(
                404, f"Товар с id={item_data.product_id} не найден"
            )
        if float(product.quantity) < item_data.quantity:
            raise HTTPException(
                400,
                f"Недостаточно товара '{product.name}': "
                f"доступно {product.quantity}, запрошено {item_data.quantity}"
            )

        # Резервирование остатка
        product.quantity = float(product.quantity) - item_data.quantity
        item_total = float(product.price) * item_data.quantity
        total_amount += item_total

        order_items.append(OrderItem(
            product_id=product.id,
            quantity=item_data.quantity,
            price_at_order=float(product.price),
        ))

    # Эмуляция оплаты (SRS 5.2: «подключение платёжного шлюза»)
    payment_success = True  # Заглушка — всегда успешно

    if not payment_success:
        raise HTTPException(402, "Ошибка оплаты. Попробуйте позже.")

    # Создание заказа
    order = Order(
        customer_id=customer.id,
        pickup_point_id=data.pickup_point_id,
        total_amount=round(total_amount, 2),
        payment_method=data.payment_method,
        payment_status=payment_success,
        status=OrderStatus.NEW,
    )
    db.add(order)
    await db.flush()

    # Привязка позиций к заказу
    for oi in order_items:
        oi.order_id = order.id
        db.add(oi)

    await db.commit()

    # Уведомление (SRS: сквозная функция «Уведомления»)
    await send_notification(
        db, current_user.id,
        "order_status",
        f"Заказ #{order.id} успешно оформлен! Ожидает подтверждения фермера."
    )

    # Возвращаем созданный заказ
    return OrderResponse(
        id=order.id,
        customer_id=order.customer_id,
        pickup_point_id=order.pickup_point_id,
        order_date=order.order_date,
        status=order.status.value,
        total_amount=float(order.total_amount),
        payment_method=order.payment_method,
        payment_status=order.payment_status,
        items=[
            OrderItemResponse(
                id=oi.id, product_id=oi.product_id,
                quantity=float(oi.quantity),
                price_at_order=float(oi.price_at_order),
            )
            for oi in order_items
        ],
    )


@router.get("/my", response_model=OrderListResponse)
async def get_my_orders(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_customer),
        status_filter: str | None = None,
        page: int = Query(1, ge=1),
        per_page: int = Query(20, ge=1, le=100),
):
    """Получение заказов текущего покупателя (UC-4)."""
    cust_result = await db.execute(
        select(Customer).where(Customer.user_id == current_user.id)
    )
    customer = cust_result.scalar_one_or_none()
    if not customer:
        raise HTTPException(404, "Профиль покупателя не найден")

    base_query = (
        select(Order)
        .where(Order.customer_id == customer.id)
    )
    if status_filter:
        base_query = base_query.where(Order.status == OrderStatus(status_filter))

    total_result = await db.execute(select(func.count()).select_from(base_query.subquery()))
    total = total_result.scalar()

    query = (
        base_query
        .options(selectinload(Order.items))
        .order_by(Order.order_date.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    result = await db.execute(query)
    orders = result.scalars().all()

    items = [
        OrderResponse(
            id=o.id, customer_id=o.customer_id,
            pickup_point_id=o.pickup_point_id,
            order_date=o.order_date,
            status=o.status.value, total_amount=float(o.total_amount),
            payment_method=o.payment_method, payment_status=o.payment_status,
            items=[
                OrderItemResponse(
                    id=i.id, product_id=i.product_id,
                    quantity=float(i.quantity),
                    price_at_order=float(i.price_at_order),
                )
                for i in o.items
            ],
        )
        for o in orders
    ]
    return OrderListResponse(items=items, total=total, page=page, per_page=per_page)


@router.get("/farmer", response_model=OrderListResponse)
async def get_farmer_orders(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_farmer),
        status_filter: str | None = None,
        page: int = Query(1, ge=1),
        per_page: int = Query(20, ge=1, le=100),
):
    """Получение заказов, содержащих товары текущего фермера (UC-6)."""
    farmer_result = await db.execute(
        select(Farmer).where(Farmer.user_id == current_user.id)
    )
    farmer = farmer_result.scalar_one_or_none()
    if not farmer:
        raise HTTPException(404, "Профиль фермера не найден")

    # Находим заказы, содержащие товары этого фермера
    base_query = (
        select(Order)
        .join(OrderItem)
        .join(Product)
        .where(Product.farmer_id == farmer.id)
        .distinct()
    )
    if status_filter:
        base_query = base_query.where(Order.status == OrderStatus(status_filter))

    total_result = await db.execute(select(func.count()).select_from(base_query.subquery()))
    total = total_result.scalar()

    query = (
        base_query
        .options(selectinload(Order.items).selectinload(OrderItem.product))
        .order_by(Order.order_date.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    result = await db.execute(query)
    orders = result.unique().scalars().all()

    items = [
        OrderResponse(
            id=o.id, customer_id=o.customer_id,
            pickup_point_id=o.pickup_point_id,
            order_date=o.order_date,
            status=o.status.value, total_amount=float(o.total_amount),
            payment_method=o.payment_method, payment_status=o.payment_status,
            items=[
                OrderItemResponse(
                    id=i.id, product_id=i.product_id,
                    product_name=i.product.name if i.product else None,
                    quantity=float(i.quantity),
                    price_at_order=float(i.price_at_order),
                )
                for i in o.items
            ],
        )
        for o in orders
    ]
    return OrderListResponse(items=items, total=total, page=page, per_page=per_page)


@router.patch("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
        order_id: int,
        data: OrderStatusUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_farmer),
):
    """
    Обновление статуса заказа фермером (UC-6).
    Подтверждение / отклонение / изменение статуса.
    """
    farmer_result = await db.execute(
        select(Farmer).where(Farmer.user_id == current_user.id)
    )
    farmer = farmer_result.scalar_one_or_none()
    if not farmer:
        raise HTTPException(404, "Профиль фермера не найден")

    result = await db.execute(
        select(Order).options(selectinload(Order.items)).where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(404, "Заказ не найден")

    # Проверяем что заказ содержит товары именно этого фермера
    farmer_items_result = await db.execute(
        select(OrderItem)
        .join(Product)
        .where(OrderItem.order_id == order.id)
        .where(Product.farmer_id == farmer.id)
    )
    if not farmer_items_result.scalars().first():
        raise HTTPException(403, "Этот заказ не содержит ваших товаров")

    new_status = OrderStatus(data.status)

    # Валидация переходов статусов
    valid_transitions = {
        OrderStatus.NEW: [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],
        OrderStatus.CONFIRMED: [OrderStatus.READY, OrderStatus.CANCELLED],
        OrderStatus.READY: [OrderStatus.DELIVERED],
    }
    if order.status not in valid_transitions:
        raise HTTPException(400, f"Заказ в статусе '{order.status.value}' нельзя изменить")
    if new_status not in valid_transitions.get(order.status, []):
        raise HTTPException(
            400,
            f"Невозможен переход из '{order.status.value}' в '{new_status.value}'"
        )

    # При отмене — возвращаем остатки
    if new_status == OrderStatus.CANCELLED:
        for item in order.items:
            product_result = await db.execute(
                select(Product).where(Product.id == item.product_id).with_for_update()
            )
            product = product_result.scalar_one()
            product.quantity = float(product.quantity) + float(item.quantity)

    order.status = new_status
    await db.commit()

    # Уведомление покупателю
    status_messages = {
        OrderStatus.CONFIRMED: f"Заказ #{order.id} подтверждён фермером!",
        OrderStatus.READY: f"Заказ #{order.id} готов к выдаче!",
        OrderStatus.DELIVERED: f"Заказ #{order.id} выдан. Спасибо за покупку!",
        OrderStatus.CANCELLED: f"Заказ #{order.id} отменён. Причина: {data.reason or 'не указана'}",
    }
    # Получаем user_id покупателя
    cust_result = await db.execute(
        select(Customer).where(Customer.id == order.customer_id)
    )
    customer = cust_result.scalar_one()
    await send_notification(
        db, customer.user_id, "order_status", status_messages[new_status]
    )

    return OrderResponse(
        id=order.id, customer_id=order.customer_id,
        pickup_point_id=order.pickup_point_id,
        order_date=order.order_date,
        status=order.status.value, total_amount=float(order.total_amount),
        payment_method=order.payment_method, payment_status=order.payment_status,
    )