from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.database.repositories.pull_request import PullRequestRepo, pull_request_repo
from app.database.repositories.user import UserRepo, user_repo
from app.exceptions import CannotReassignPrException, ModelExistException, NotFoundException
from app.schemas.pull_request import (
    PullRequestCreateRequest,
    PullRequestMergeRequest,
    PullRequestReassignRequest,
    PullRequestReassignResponse,
    PullRequestResponse,
)
from app.services.pull_request import PullRequestService

router = APIRouter(prefix='/pullRequest', tags=['PullRequests'])


def get_pr_service(
    pr_repository: Annotated[PullRequestRepo, Depends(lambda: pull_request_repo)],
    user_repository: Annotated[UserRepo, Depends(lambda: user_repo)],
) -> PullRequestService:
    """Фабрика для создания сервиса Pull Requests с внедрёнными зависимостями."""
    return PullRequestService(pr_repo=pr_repository, user_repo=user_repository)


@router.post(
    '/create',
    status_code=status.HTTP_201_CREATED,
    summary='Создать PR и автоматически назначить до 2 ревьюверов из команды автора',
)
async def create_pull_request(
    request: PullRequestCreateRequest,
    pr_service: Annotated[PullRequestService, Depends(get_pr_service)],
) -> dict[str, PullRequestResponse]:
    """
    Создать Pull Request и автоматически назначить ревьюверов.
    Автоматически назначает до 2 активных ревьюверов из команды автора.
    """
    try:
        pr = await pr_service.create_pull_request(
            pull_request_id=request.pull_request_id,
            pull_request_name=request.pull_request_name,
            author_id=request.author_id,
        )
        return {'pr': pr}
    except ModelExistException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                'error': {
                    'code': 'PR_EXISTS',
                    'message': 'PR id already exists',
                }
            },
        ) from e
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'resource not found',
                }
            },
        ) from e


@router.post(
    '/merge',
    status_code=status.HTTP_200_OK,
    summary='Пометить PR как MERGED (идемпотентная операция)',
)
async def merge_pull_request(
    request: PullRequestMergeRequest,
    pr_service: Annotated[PullRequestService, Depends(get_pr_service)],
) -> dict[str, PullRequestResponse]:
    """
    Пометить PR как MERGED. Повторный вызов вернет тот же результат.
    """
    try:
        pr = await pr_service.merge_pull_request(request.pull_request_id)
        return {'pr': pr}
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'resource not found',
                }
            },
        ) from e


@router.post(
    '/reassign',
    status_code=status.HTTP_200_OK,
    summary='Переназначить конкретного ревьювера на другого из его команды',
)
async def reassign_reviewer(
    request: PullRequestReassignRequest,
    pr_service: Annotated[PullRequestService, Depends(get_pr_service)],
) -> PullRequestReassignResponse:
    """
    Переназначить ревьювера.

    Правила:
    - Нельзя переназначить после MERGED
    - Ревьювер должен быть назначен на PR
    - Должны быть доступные кандидаты
    """
    try:
        return await pr_service.reassign_reviewer(
            pull_request_id=request.pull_request_id,
            old_user_id=request.old_user_id,
        )
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'resource not found',
                }
            },
        ) from e
    except CannotReassignPrException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                'error': {
                    'code': 'PR_MERGED',
                    'message': 'cannot reassign on merged PR',
                }
            },
        ) from e
