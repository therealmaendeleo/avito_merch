"""Dependencies для FastAPI endpoints."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.schemas.auth import TokenData
from app.utils.auth import decode_access_token

# Bearer token схема
security = HTTPBearer()


async def get_current_employee(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> TokenData:
    """
    Получение текущего аутентифицированного сотрудника из JWT токена.

    Args:
        credentials: Bearer токен из заголовка Authorization

    Returns:
        Данные сотрудника из токена

    Raises:
        HTTPException: 401 если токен невалиден или отсутствует
    """
    token = credentials.credentials

    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Невалидный или истекший токен',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    employee_id: int | None = payload.get('sub')
    username: str | None = payload.get('username')

    if employee_id is None or username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Невалидная структура токена',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    return TokenData(employee_id=employee_id, username=username)
