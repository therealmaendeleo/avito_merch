"""Схемы для аутентификации и авторизации."""

from pydantic import BaseModel, Field


class AuthRequest(BaseModel):
    """Запрос на аутентификацию."""

    username: str
    password: str = Field(..., min_length=6, max_length=100, description='Пароль')


class AuthResponse(BaseModel):
    """Ответ с JWT токеном."""

    access_token: str = Field(..., description='JWT токен доступа')
    token_type: str = Field(default='bearer', description='Тип токена')
    expires_in: int = Field(..., description='Время жизни токена в секундах')


class TokenData(BaseModel):
    """Данные из JWT токена."""

    employee_id: int = Field(..., description='ID сотрудника')
    username: str = Field(..., description='Username сотрудника')


class ErrorResponse(BaseModel):
    """Ответ с ошибкой."""

    code: int = Field(..., description='Код ошибки')
    detail: str = Field(..., description='Описание ошибки')

    model_config = {
        'json_schema_extra': {
            'examples': [
                {
                    'code': 401,
                    'detail': 'Неверный email или пароль',
                }
            ]
        }
    }
