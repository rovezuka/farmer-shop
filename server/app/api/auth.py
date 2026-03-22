"""
Роутер аутентификации и регистрации.
Соответствует: SRS раздел 3.2 UC-1 (регистрация), сквозная функция «Аутентификация».
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.user import User, UserRole
from app.models.customer import Customer
from app.models.farmer import Farmer
from app.schemas.auth import (
    UserRegister, UserLogin, TokenResponse, TokenRefresh,
    CustomerUpdate, CustomerResponse, FarmerUpdate, FarmerResponse,
)
from app.core.security import (
    get_password_hash, verify_password,
    create_access_token, create_refresh_token, decode_token,
)
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Аутентификация"])


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    """
    Регистрация нового пользователя (UC-1).

    Принимает email, пароль, роль и профильные данные.
    Возвращает JWT-токены.
    """
    # Проверка уникальности email
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким email уже существует"
        )

    # Создание пользователя
    user = User(
        email=data.email,
        password_hash=get_password_hash(data.password),
        role=UserRole(data.role),
    )
    db.add(user)
    await db.flush()  # Получаем user.id

    # Создание профиля в зависимости от роли
    if data.role == "customer":
        if not data.first_name:
            raise HTTPException(400, detail="Укажите имя для покупателя")
        customer = Customer(
            user_id=user.id,
            first_name=data.first_name,
            phone=data.phone,
        )
        db.add(customer)
    elif data.role == "farmer":
        if not data.farm_name:
            raise HTTPException(400, detail="Укажите название хозяйства")
        farmer = Farmer(
            user_id=user.id,
            farm_name=data.farm_name,
            farm_address=data.farm_address,
            phone=data.phone,
            is_verified=False,  # Требуется верификация (UC-8)
        )
        db.add(farmer)

    await db.commit()

    # Генерация токенов
    token_data = {"sub": str(user.id), "role": user.role.value}
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
        role=user.role.value,
        user_id=user.id,
    )


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Вход в систему.
    Проверяет email и пароль, возвращает JWT-токены.
    """
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
        )

    token_data = {"sub": str(user.id), "role": user.role.value}
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
        role=user.role.value,
        user_id=user.id,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(data: TokenRefresh, db: AsyncSession = Depends(get_db)):
    """Обновление access-токена по refresh-токену."""
    payload = decode_token(data.refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(400, detail="Передан не refresh-токен")

    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(401, detail="Пользователь не найден")

    token_data = {"sub": str(user.id), "role": user.role.value}
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
        role=user.role.value,
        user_id=user.id,
    )


@router.patch("/me/customer", response_model=CustomerResponse)
async def update_customer_profile(
    data: CustomerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Обновление профиля покупателя."""
    if current_user.role != UserRole.CUSTOMER:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Доступ только для покупателей")

    result = await db.execute(select(Customer).where(Customer.user_id == current_user.id))
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Профиль покупателя не найден")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(customer, field, value)

    await db.commit()
    await db.refresh(customer)
    return customer


@router.patch("/me/farmer", response_model=FarmerResponse)
async def update_farmer_profile(
    data: FarmerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Обновление профиля фермера."""
    if current_user.role != UserRole.FARMER:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Доступ только для фермеров")

    result = await db.execute(select(Farmer).where(Farmer.user_id == current_user.id))
    farmer = result.scalar_one_or_none()
    if not farmer:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Профиль фермера не найден")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(farmer, field, value)

    await db.commit()
    await db.refresh(farmer)
    return farmer