"""
Сервис уведомлений (SRS раздел 3.1 «Сквозные функции — Уведомления»).
В MVP реализовано как запись в БД + лог в консоль.
В продакшн заменить на SMTP / SMS / push.
"""
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.notification import Notification

logger = logging.getLogger("notifications")


async def send_notification(
    db: AsyncSession,
    user_id: int,
    notification_type: str,
    message: str,
):
    """
    Отправляет уведомление пользователю.
    Пока — запись в БД и лог в консоль.
    """
    notification = Notification(
        user_id=user_id,
        type=notification_type,
        message=message,
    )
    db.add(notification)
    await db.flush()

    # Логирование вместо реальной отправки
    logger.info(f"📧 Уведомление для user_id={user_id}: [{notification_type}] {message}")

    # TODO: Интеграция с SMTP (fastapi-mail) или SMS-шлюзом
    # from fastapi_mail import FastMail, MessageSchema
    # ...