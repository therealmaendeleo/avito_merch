from app.database.repositories.user import UserRepo
from app.exceptions import NotFoundException
from app.schemas.user import PullRequestShort, UserResponse, UserReviewsResponse


class UserService:
    def __init__(self, user_repo: UserRepo) -> None:
        self.user_repo = user_repo

    async def set_is_active(self, user_id: str, is_active: bool) -> UserResponse:
        """
        Устанавливает флаг активности пользователя.

        :raises NotFoundException: Пользователь не найден.
        """
        user = await self.user_repo.update_is_active(user_id=user_id, is_active=is_active)
        if not user:
            raise NotFoundException()

        return UserResponse(
            user_id=user.user_id,
            username=user.username,
            team_name=user.team_name,
            is_active=user.is_active,
        )

    async def get_reviews(self, user_id: str) -> UserReviewsResponse:
        """
        Возвращает все PR, где пользователь назначен ревьювером.

        :raises NotFoundException: Пользователь не найден.
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException()

        pull_requests = await self.user_repo.get_assigned_pull_requests(user_id)

        pr_short_list = [
            PullRequestShort(
                pull_request_id=pr.pull_request_id,
                pull_request_name=pr.pull_request_name,
                author_id=pr.author_id,
                status=pr.status,
            )
            for pr in pull_requests
        ]

        return UserReviewsResponse(
            user_id=user_id,
            pull_requests=pr_short_list,
        )


user_service = UserService(user_repo=UserRepo())
