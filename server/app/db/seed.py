"""
Скрипт для наполнения БД тестовыми данными.
Запуск: python -m app.db.seed
"""
import asyncio
from datetime import date, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import async_session, engine, Base
from app.models import *
from app.core.security import get_password_hash


async def seed():
    async with async_session() as session:
        # --- Категории (SRS 4.2) ---
        categories = [
            Category(id=1, name="Овощи", description="Свежие овощи с грядки"),
            Category(id=2, name="Фрукты", description="Сезонные фрукты"),
            Category(id=3, name="Молочная продукция", description="Молоко, сыр, творог"),
            Category(id=4, name="Мясо и птица", description="Фермерское мясо"),
            Category(id=5, name="Мёд и варенье", description="Натуральный мёд"),
            Category(id=6, name="Яйца", description="Домашние яйца"),
            Category(id=7, name="Зелень", description="Свежая зелень", parent_id=1),
        ]
        session.add_all(categories)

        # --- Пользователи ---
        # Администратор
        admin_user = User(
            id=1, email="admin@ferma.ru",
            password_hash=get_password_hash("admin123"),
            role=UserRole.ADMIN
        )
        # Фермер 1
        farmer_user1 = User(
            id=2, email="ivanov@ferma.ru",
            password_hash=get_password_hash("farmer123"),
            role=UserRole.FARMER
        )
        # Фермер 2
        farmer_user2 = User(
            id=3, email="petrova@ferma.ru",
            password_hash=get_password_hash("farmer123"),
            role=UserRole.FARMER
        )
        # Покупатель
        customer_user = User(
            id=4, email="buyer@example.com",
            password_hash=get_password_hash("buyer123"),
            role=UserRole.CUSTOMER
        )
        session.add_all([admin_user, farmer_user1, farmer_user2, customer_user])
        await session.flush()

        # --- Профили ---
        farmer1 = Farmer(
            user_id=2, farm_name='Ферма Иванова',
            farm_address='Ленинградская обл., д. Заречье',
            phone='+79110001122', is_verified=True,
            latitude=59.8, longitude=30.2
        )
        farmer2 = Farmer(
            user_id=3, farm_name='Эко-сад Петровых',
            farm_address='Ленинградская обл., пос. Луговое',
            phone='+79110003344', is_verified=True,
            latitude=59.95, longitude=30.5
        )
        customer = Customer(
            user_id=4, first_name='Алексей',
            phone='+79215551234',
            latitude=59.9343, longitude=30.3351  # Центр СПб
        )
        session.add_all([farmer1, farmer2, customer])
        await session.flush()

        # --- Точки выдачи (UC-9) ---
        points = [
            PickupPoint(
                name='Продукты 24', address='СПб, Невский пр., 100',
                latitude=59.9311, longitude=30.3609,
                working_hours='09:00-21:00 ежедневно', is_active=True
            ),
            PickupPoint(
                name='Фермерский рынок', address='СПб, ул. Садовая, 50',
                latitude=59.9271, longitude=30.3167,
                working_hours='08:00-20:00 Пн-Сб', is_active=True
            ),
            PickupPoint(
                name='Магазин у дома', address='СПб, пр. Стачек, 15',
                latitude=59.8985, longitude=30.2615,
                working_hours='10:00-22:00 ежедневно', is_active=True
            ),
        ]
        session.add_all(points)
        await session.flush()

        # --- Товары (UC-5) ---
        products = [
            Product(
                farmer_id=farmer1.id, category_id=1, name='Помидоры Бычье сердце',
                description='Крупные сочные помидоры, выращенные без химии',
                price=280.00, unit=ProductUnit.KG, quantity=50,
                expiration_date=date.today() + timedelta(days=7),
                status=ProductStatus.ACTIVE,
                image_url='/static/images/tomato.jpg'
            ),
            Product(
                farmer_id=farmer1.id, category_id=1, name='Огурцы грунтовые',
                description='Хрустящие огурчики с грядки',
                price=150.00, unit=ProductUnit.KG, quantity=30,
                expiration_date=date.today() + timedelta(days=5),
                status=ProductStatus.ACTIVE,
            ),
            Product(
                farmer_id=farmer1.id, category_id=3, name='Молоко коровье 3.2%',
                description='Натуральное молоко от домашних коров',
                price=90.00, unit=ProductUnit.LITER, quantity=20,
                expiration_date=date.today() + timedelta(days=3),
                status=ProductStatus.ACTIVE,
            ),
            Product(
                farmer_id=farmer2.id, category_id=2, name='Яблоки Антоновка',
                description='Кислые яблоки для пирогов и компотов',
                price=120.00, unit=ProductUnit.KG, quantity=100,
                expiration_date=date.today() + timedelta(days=14),
                status=ProductStatus.ACTIVE,
            ),
            Product(
                farmer_id=farmer2.id, category_id=5, name='Мёд цветочный',
                description='Натуральный мёд с собственной пасеки',
                price=650.00, unit=ProductUnit.KG, quantity=15,
                expiration_date=date.today() + timedelta(days=365),
                status=ProductStatus.ACTIVE,
            ),
            Product(
                farmer_id=farmer2.id, category_id=6, name='Яйца куриные (10 шт)',
                description='Домашние яйца от кур свободного выгула',
                price=180.00, unit=ProductUnit.PIECE, quantity=200,
                expiration_date=date.today() + timedelta(days=21),
                status=ProductStatus.ACTIVE,
            ),
        ]
        session.add_all(products)
        await session.commit()
        print("✅ Тестовые данные успешно загружены!")


async def main():
    async with engine.begin() as conn:
        # Пересоздание таблиц (только для разработки!)
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    await seed()


if __name__ == "__main__":
    asyncio.run(main())