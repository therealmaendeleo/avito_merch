"""API endpoints для аутентификации."""

from fastapi import APIRouter, HTTPException, status

from app.schemas.auth import AuthRequest, AuthResponse, ErrorResponse
from app.services.employee import employee_service

router = APIRouter(prefix='/api', tags=['Authentication'])


@router.post(
    '/auth',
    response_model=AuthResponse,
    responses={
        200: {
            'description': 'Успешная аутентификация',
            'model': AuthResponse,
        },
        400: {
            'description': 'Неверный запрос',
            'model': ErrorResponse,
        },
        401: {
            'description': 'Неавторизован (неверный пароль)',
            'model': ErrorResponse,
        },
        500: {
            'description': 'Внутренняя ошибка сервера',
            'model': ErrorResponse,
        },
    },
)
async def auth_user(auth_data: AuthRequest) -> AuthResponse:
    try:
        return await employee_service.authenticate_or_create(auth_data)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        ) from e
