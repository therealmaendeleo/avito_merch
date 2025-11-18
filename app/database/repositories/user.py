from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.database.base import BasePgInterface, with_session, with_session_commit
from app.database.models import PullRequest, PullRequestReviewer, User


class UserRepo(BasePgInterface):
    """Репозиторий для работы с пользователями."""

    @with_session
    async def get_by_id(
        self,
        user_id: str,
        session: AsyncSession | None = None,
    ) -> User | None:
        """Получить пользователя по ID."""
        query = select(User).where(User.user_id == user_id)
        result = await session.execute(query)  # type: ignore
        return result.scalar_one_or_none()

    @with_session_commit
    async def create_or_update(
        self,
        user_id: str,
        username: str,
        team_name: str,
        is_active: bool,
        session: AsyncSession | None = None,
    ) -> User:
        """Создать нового пользователя или обновить существующего."""
        existing_user = await self.get_by_id(user_id, session=session)

        if existing_user:
            existing_user.username = username
            existing_user.team_name = team_name
            existing_user.is_active = is_active
            await session.flush()  # type: ignore
            await session.refresh(existing_user)  # type: ignore
            return existing_user
        else:
            user = User(
                user_id=user_id,
                username=username,
                team_name=team_name,
                is_active=is_active,
            )
            session.add(user)  # type: ignore
            await session.flush()  # type: ignore
            await session.refresh(user)  # type: ignore
            return user

    @with_session_commit
    async def update_is_active(
        self,
        user_id: str,
        is_active: bool,
        session: AsyncSession | None = None,
    ) -> User | None:
        """Обновить флаг активности пользователя."""
        user = await self.get_by_id(user_id, session=session)
        if user:
            user.is_active = is_active
            await session.flush()  # type: ignore
            await session.refresh(user)  # type: ignore
        return user

    @with_session
    async def get_assigned_pull_requests(
        self,
        user_id: str,
        session: AsyncSession | None = None,
    ) -> list[PullRequest]:
        """Получить все PR, где пользователь назначен ревьювером."""
        query = (
            select(PullRequest)
            .join(PullRequestReviewer, PullRequest.pull_request_id == PullRequestReviewer.pull_request_id)
            .where(PullRequestReviewer.user_id == user_id)
            .options(joinedload(PullRequest.author))
        )
        result = await session.execute(query)  # type: ignore
        return list(result.unique().scalars().all())


user_repo = UserRepo()
