from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.database.repositories.team import TeamRepo, team_repo
from app.database.repositories.user import UserRepo, user_repo
from app.exceptions import ModelExistException, NotFoundException
from app.schemas.team import TeamCreate, TeamResponse
from app.services.team import TeamService

router = APIRouter(prefix='/team', tags=['Teams'])


def get_team_service(
    team_repository: Annotated[TeamRepo, Depends(lambda: team_repo)],
    user_repository: Annotated[UserRepo, Depends(lambda: user_repo)],
) -> TeamService:
    """Фабрика для создания сервиса команд с внедрёнными зависимостями."""
    return TeamService(team_repo=team_repository, user_repo=user_repository)


@router.post(
    '/add',
    status_code=status.HTTP_201_CREATED,
    summary='Создать команду с участниками',
)
async def add_team(
    team_data: TeamCreate,
    team_service: Annotated[TeamService, Depends(get_team_service)],
) -> dict[str, TeamResponse]:
    try:
        team = await team_service.add_team(team_data)
        return {'team': team}
    except ModelExistException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                'error': {
                    'code': 'TEAM_EXISTS',
                    'message': 'team_name already exists',
                }
            },
        ) from e


@router.get(
    '/get',
    status_code=status.HTTP_200_OK,
    response_model=TeamResponse,
    summary='Получить команду по имени',
)
async def get_team(
    team_name: Annotated[str, Query()],
    team_service: Annotated[TeamService, Depends(get_team_service)],
) -> TeamResponse:
    try:
        return await team_service.get_team(team_name)
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
