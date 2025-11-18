from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.database.base import BasePgInterface, with_session, with_session_commit
from app.database.models import PRStatus, PullRequest, PullRequestReviewer, User


class PullRequestRepo(BasePgInterface):
    """Репозиторий для работы с Pull Requests."""

    @with_session
    async def get_by_id(
        self,
        pull_request_id: str,
        session: AsyncSession | None = None,
    ) -> PullRequest | None:
        """Получить PR по ID с загруженными связями."""
        query = (
            select(PullRequest)
            .where(PullRequest.pull_request_id == pull_request_id)
            .options(
                joinedload(PullRequest.author),
                joinedload(PullRequest.reviewer_assignments),
            )
        )
        result = await session.execute(query)  # type: ignore
        return result.unique().scalar_one_or_none()

    @with_session
    async def exists(
        self,
        pull_request_id: str,
        session: AsyncSession | None = None,
    ) -> bool:
        """Проверить существование PR."""
        query = select(PullRequest.pull_request_id).where(PullRequest.pull_request_id == pull_request_id)
        result = await session.execute(query)  # type: ignore
        return result.scalar_one_or_none() is not None

    @with_session_commit
    async def create(
        self,
        pull_request_id: str,
        pull_request_name: str,
        author_id: str,
        session: AsyncSession | None = None,
    ) -> PullRequest:
        """Создать новый PR."""
        pr = PullRequest(
            pull_request_id=pull_request_id,
            pull_request_name=pull_request_name,
            author_id=author_id,
            status=PRStatus.OPEN.value,
        )
        session.add(pr)  # type: ignore
        await session.flush()  # type: ignore
        await session.refresh(pr)  # type: ignore
        return pr

    @with_session_commit
    async def add_reviewer(
        self,
        pull_request_id: str,
        user_id: str,
        session: AsyncSession | None = None,
    ) -> None:
        """Добавить ревьювера к PR."""
        reviewer = PullRequestReviewer(
            pull_request_id=pull_request_id,
            user_id=user_id,
        )
        session.add(reviewer)  # type: ignore
        await session.flush()  # type: ignore

    @with_session_commit
    async def remove_reviewer(
        self,
        pull_request_id: str,
        user_id: str,
        session: AsyncSession | None = None,
    ) -> None:
        """Удалить ревьювера из PR."""
        query = select(PullRequestReviewer).where(
            PullRequestReviewer.pull_request_id == pull_request_id,
            PullRequestReviewer.user_id == user_id,
        )
        result = await session.execute(query)  # type: ignore
        reviewer = result.scalar_one_or_none()
        if reviewer:
            await session.delete(reviewer)  # type: ignore
            await session.flush()  # type: ignore

    @with_session
    async def get_reviewers(
        self,
        pull_request_id: str,
        session: AsyncSession | None = None,
    ) -> list[str]:
        """Получить список ID ревьюверов PR."""
        query = select(PullRequestReviewer.user_id).where(PullRequestReviewer.pull_request_id == pull_request_id)
        result = await session.execute(query)  # type: ignore
        return list(result.scalars().all())

    @with_session_commit
    async def merge(
        self,
        pull_request_id: str,
        session: AsyncSession | None = None,
    ) -> PullRequest | None:
        """Пометить PR как MERGED (идемпотентная операция)."""
        pr = await self.get_by_id(pull_request_id, session=session)
        if pr is None:
            return None

        # Идемпотентность: если уже MERGED, просто возвращаем
        if pr.status == PRStatus.MERGED.value:
            return pr

        pr.status = PRStatus.MERGED.value
        pr.merged_at = datetime.now()  # timezone-naive для совместимости с TIMESTAMP WITHOUT TIME ZONE
        await session.flush()  # type: ignore
        await session.refresh(pr)  # type: ignore
        return pr

    @with_session
    async def get_active_team_members(
        self,
        team_name: str,
        exclude_user_id: str | None = None,
        session: AsyncSession | None = None,
    ) -> list[User]:
        """Получить активных участников команды (опционально исключая пользователя)."""
        query = select(User).where(User.team_name == team_name, User.is_active == True)  # noqa: E712

        if exclude_user_id:
            query = query.where(User.user_id != exclude_user_id)

        result = await session.execute(query)  # type: ignore
        return list(result.scalars().all())


pull_request_repo = PullRequestRepo()
