import secrets

from app.database.models import PRStatus
from app.database.repositories.pull_request import PullRequestRepo
from app.database.repositories.user import UserRepo
from app.exceptions import CannotReassignPrException, ModelExistException, NotFoundException
from app.schemas.pull_request import (
    PullRequestReassignResponse,
    PullRequestResponse,
)


class PullRequestService:
    def __init__(self, pr_repo: PullRequestRepo, user_repo: UserRepo) -> None:
        self.pr_repo = pr_repo
        self.user_repo = user_repo

    async def create_pull_request(
        self,
        pull_request_id: str,
        pull_request_name: str,
        author_id: str,
    ) -> PullRequestResponse:
        """
        Создать PR и автоматически назначить до 2 ревьюверов.

        :raises ModelExistException: Pull Request уже существует.
        :raises NotFoundException: Автор не найден.
        """
        if await self.pr_repo.exists(pull_request_id):
            raise ModelExistException()

        author = await self.user_repo.get_by_id(author_id)
        if not author:
            raise NotFoundException()

        pr = await self.pr_repo.create(
            pull_request_id=pull_request_id,
            pull_request_name=pull_request_name,
            author_id=author_id,
        )

        reviewer_ids = await self._assign_reviewers(
            pr.pull_request_id,
            author.team_name,
            author_id,
            max_reviewers=2,
        )
        return self._build_response(pr, reviewer_ids)

    async def merge_pull_request(self, pull_request_id: str) -> PullRequestResponse:
        """
        Пометить PR как MERGED.

        :raises NotFoundException: Если PR не найден.
        """
        pr = await self.pr_repo.merge(pull_request_id)
        if not pr:
            raise NotFoundException()

        reviewers = await self.pr_repo.get_reviewers(pull_request_id)
        return self._build_response(pr, reviewers)

    async def reassign_reviewer(
        self,
        pull_request_id: str,
        old_user_id: str,
    ) -> PullRequestReassignResponse:
        """
        Переназначить ревьювера на другого из его команды.

        :raises NotFoundException: Не найден PR или ревьювер.
        :raises CannotReassignPrException: Нарушение правил переназначения PR.
        """
        # Получаем PR
        pr = await self.pr_repo.get_by_id(pull_request_id)
        if not pr:
            raise NotFoundException()

        if pr.status == PRStatus.MERGED.value:
            raise CannotReassignPrException()

        current_reviewers = await self.pr_repo.get_reviewers(pull_request_id)
        if old_user_id not in current_reviewers:
            raise CannotReassignPrException()

        old_reviewer = await self.user_repo.get_by_id(old_user_id)
        if old_reviewer is None:
            raise NotFoundException()

        exclude_ids = [pr.author_id, *current_reviewers]
        candidates = await self.pr_repo.get_active_team_members(
            team_name=old_reviewer.team_name,
            exclude_user_id=None,
        )
        available_candidates = [c for c in candidates if c.user_id not in exclude_ids]

        if not available_candidates:
            raise CannotReassignPrException()

        new_reviewer = available_candidates[secrets.randbelow(len(available_candidates))]

        await self.pr_repo.remove_reviewer(pull_request_id, old_user_id)
        await self.pr_repo.add_reviewer(pull_request_id, new_reviewer.user_id)

        updated_reviewers = await self.pr_repo.get_reviewers(pull_request_id)
        updated_pr = await self.pr_repo.get_by_id(pull_request_id)

        return PullRequestReassignResponse(
            pr=self._build_response(updated_pr, updated_reviewers),
            replaced_by=new_reviewer.user_id,
        )

    async def _assign_reviewers(
        self,
        pull_request_id: str,
        team_name: str,
        author_id: str,
        max_reviewers: int = 2,
    ) -> list[str]:
        """
        Назначить до N ревьюверов из команды (исключая автора, только активные).

        :returns: Список ID назначенных ревьюверов.
        """
        candidates = await self.pr_repo.get_active_team_members(
            team_name=team_name,
            exclude_user_id=author_id,
        )

        selected_count = min(len(candidates), max_reviewers)
        if candidates:
            indices = list(range(len(candidates)))
            selected_indices = []
            for _ in range(selected_count):
                idx = secrets.randbelow(len(indices))
                selected_indices.append(indices.pop(idx))
            selected_reviewers = [candidates[i] for i in selected_indices]
        else:
            selected_reviewers = []

        reviewer_ids = []
        for reviewer in selected_reviewers:
            await self.pr_repo.add_reviewer(pull_request_id, reviewer.user_id)
            reviewer_ids.append(reviewer.user_id)

        return reviewer_ids

    def _build_response(self, pr, reviewers: list[str]) -> PullRequestResponse:
        return PullRequestResponse(
            pull_request_id=pr.pull_request_id,
            pull_request_name=pr.pull_request_name,
            author_id=pr.author_id,
            status=pr.status,
            assigned_reviewers=reviewers,
            createdAt=pr.created_at,
            mergedAt=pr.merged_at,
        )


pull_request_service = PullRequestService(
    pr_repo=PullRequestRepo(),
    user_repo=UserRepo(),
)
