from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.base import BasePgInterface, with_session, with_session_commit
from app.database.models import Team


class TeamRepo(BasePgInterface):
    """Репозиторий для работы с командами."""

    @with_session
    async def get_by_name(
        self,
        team_name: str,
        session: AsyncSession | None = None,
    ) -> Team | None:
        """Получить команду по имени с загрузкой участников."""
        query = select(Team).where(Team.team_name == team_name).options(selectinload(Team.members))
        result = await session.execute(query)  # type: ignore
        return result.scalar_one_or_none()

    @with_session
    async def exists(
        self,
        team_name: str,
        session: AsyncSession | None = None,
    ) -> bool:
        """Проверить существование команды."""
        query = select(Team.team_name).where(Team.team_name == team_name)
        result = await session.execute(query)  # type: ignore
        return result.scalar_one_or_none() is not None

    @with_session_commit
    async def create(
        self,
        team_name: str,
        session: AsyncSession | None = None,
    ) -> Team:
        """Создать новую команду."""
        team = Team(team_name=team_name)
        session.add(team)  # type: ignore
        await session.flush()  # type: ignore
        await session.refresh(team)  # type: ignore
        return team


team_repo = TeamRepo()
