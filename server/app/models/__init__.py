"""Центральный импорт всех моделей для Alembic и создания таблиц."""
from app.models.user import User, UserRole
from app.models.customer import Customer
from app.models.farmer import Farmer
from app.models.category import Category
from app.models.product import Product, ProductStatus, ProductUnit
from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.pickup_point import PickupPoint
from app.models.review import Review
from app.models.notification import Notification

__all__ = [
    "User", "UserRole",
    "Customer", "Farmer",
    "Category", "Product", "ProductStatus", "ProductUnit",
    "Order", "OrderStatus", "OrderItem",
    "PickupPoint", "Review", "Notification",
]