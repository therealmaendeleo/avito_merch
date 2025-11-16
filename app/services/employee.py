"""Сервисный слой для работы с сотрудниками."""

from datetime import timedelta

from app.config import settings
from app.database.repositories.employee import employee_repo
from app.schemas.auth import AuthRequest, AuthResponse
from app.utils.auth import create_access_token, get_password_hash, verify_password


class EmployeeService:
    """Сервис для работы с сотрудниками."""

    def __init__(self) -> None:
        self.repo = employee_repo

    async def authenticate_or_create(self, auth_data: AuthRequest) -> AuthResponse:
        """
        Аутентификация пользователя с автоматическим созданием при первом входе.

        Логика:
        1. Ищем пользователя по username
        2. Если не найден - создаем нового с переданным паролем
        3. Если найден - проверяем пароль
        4. Генерируем JWT токен

        Args:
            auth_data: Данные для аутентификации (username и password)

        Returns:
            AuthResponse с JWT токеном

        Raises:
            ValueError: Если пользователь существует, но пароль неверный
        """
        # Ищем пользователя
        employee = await self.repo.get(username=auth_data.username)

        if employee is None:
            # Пользователь не найден - создаем нового
            hashed_password = get_password_hash(auth_data.password)
            employee = await self.repo.create(
                username=auth_data.username,
                hashed_password=hashed_password,
                balance=1000,
            )
        elif not verify_password(auth_data.password, employee.hashed_password):
            # Пользователь найден, но пароль неверный
            raise ValueError('Неверный пароль')

        # Создаем JWT токен
        access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                'sub': employee.id,  # subject - ID сотрудника
                'username': employee.name,
            },
            expires_delta=access_token_expires,
        )

        return AuthResponse(
            access_token=access_token,
            token_type='bearer',
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # в секундах
        )


# Singleton instance
employee_service = EmployeeService()