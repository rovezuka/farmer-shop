"""
Pydantic-схемы для регистрации и аутентификации.
Соответствует: SRS раздел 3.2 UC-1 (регистрация).
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
import re


class UserRegister(BaseModel):
    """Схема регистрации нового пользователя."""
    email: EmailStr
    password: str = Field(min_length=6, max_length=100)
    role: str = Field(default="customer", pattern="^(customer|farmer)$")
    # Данные покупателя (если role == customer)
    first_name: str | None = Field(None, min_length=1, max_length=50)
    phone: str | None = Field(None, max_length=12)
    # Данные фермера (если role == farmer)
    farm_name: str | None = Field(None, max_length=150)
    farm_address: str | None = Field(None, max_length=250)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        if v and not re.match(r"^\+7\d{10}$", v):
            raise ValueError("Телефон должен быть в формате +7XXXXXXXXXX")
        return v


class UserLogin(BaseModel):
    """Схема входа в систему."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Ответ с токенами."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role: str
    user_id: int


class TokenRefresh(BaseModel):
    """Запрос на обновление токена."""
    refresh_token: str


class CustomerUpdate(BaseModel):
    """Обновление профиля покупателя."""
    first_name: str | None = Field(None, min_length=1, max_length=50)
    phone: str | None = Field(None, max_length=12)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        if v and not re.match(r"^\+7\d{10}$", v):
            raise ValueError("Телефон должен быть в формате +7XXXXXXXXXX")
        return v


class CustomerResponse(BaseModel):
    """Ответ с данными профиля покупателя."""
    id: int
    first_name: str
    phone: str | None

    model_config = {"from_attributes": True}


class FarmerUpdate(BaseModel):
    """Обновление профиля фермера."""
    farm_name: str | None = Field(None, max_length=150)
    farm_address: str | None = Field(None, max_length=250)
    phone: str | None = Field(None, max_length=12)
    latitude: float | None = None
    longitude: float | None = None


class FarmerResponse(BaseModel):
    """Ответ с данными профиля фермера."""
    id: int
    farm_name: str
    farm_address: str | None
    phone: str | None
    is_verified: bool
    latitude: float | None
    longitude: float | None

    model_config = {"from_attributes": True}