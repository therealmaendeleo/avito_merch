"""Пример защищенного эндпоинта с JWT авторизацией."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_employee
from app.schemas.auth import TokenData

router = APIRouter(prefix='/api', tags=['Example'])


@router.get('/me', summary='Получить информацию о текущем пользователе')
async def get_me(
    current_employee: Annotated[TokenData, Depends(get_current_employee)],
) -> dict:
    """
    Пример защищенного эндпоинта.

    Требует Bearer токен в заголовке Authorization.

    Args:
        current_employee: Данные текущего аутентифицированного сотрудника

    Returns:
        Информация о текущем пользователе
    """
    return {
        'employee_id': current_employee.employee_id,
        'username': current_employee.username,
        'message': 'Вы успешно авторизованы!',
    }
