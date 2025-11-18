from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.database.repositories.user import UserRepo, user_repo
from app.exceptions import NotFoundException
from app.schemas.user import SetIsActiveRequest, UserResponse, UserReviewsResponse
from app.services.user import UserService

router = APIRouter(prefix='/users', tags=['Users'])


def get_user_service(
    user_repository: Annotated[UserRepo, Depends(lambda: user_repo)],
) -> UserService:
    """Фабрика для создания сервиса пользователей с внедрёнными зависимостями."""
    return UserService(user_repo=user_repository)


@router.post(
    '/setIsActive',
    status_code=status.HTTP_200_OK,
    response_model=dict[str, UserResponse],
    summary='Установить флаг активности пользователя',
)
async def set_is_active(
    request: SetIsActiveRequest,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> dict[str, UserResponse]:
    try:
        user = await user_service.set_is_active(
            user_id=request.user_id,
            is_active=request.is_active,
        )
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                'error': {
                    'code': 'TEAM_EXISTS',
                    'message': 'team_name already exists',
                }
            },
        ) from e

    return {'user': user}


@router.get(
    '/getReview',
    status_code=status.HTTP_200_OK,
    summary="Получить PR'ы, где пользователь назначен ревьювером",
)
async def get_assigned_pull_requests(
    user_id: Annotated[str, Query()],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> UserReviewsResponse:
    try:
        return await user_service.get_reviews(user_id)

    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                'error': {
                    'code': 'TEAM_EXISTS',
                    'message': 'team_name already exists',
                }
            },
        ) from e
