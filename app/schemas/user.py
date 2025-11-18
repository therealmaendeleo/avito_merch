"""Схемы для работы с пользователями."""

from pydantic import BaseModel, Field


class SetIsActiveRequest(BaseModel):
    """Запрос на изменение статуса активности пользователя."""

    user_id: str = Field(..., description='Идентификатор пользователя')
    is_active: bool = Field(..., description='Флаг активности')


class UserResponse(BaseModel):
    """Ответ с данными пользователя."""

    user_id: str = Field(..., description='Идентификатор пользователя')
    username: str = Field(..., description='Имя пользователя')
    team_name: str = Field(..., description='Название команды')
    is_active: bool = Field(..., description='Флаг активности')

    class Config:
        from_attributes = True


class PullRequestShort(BaseModel):
    """Краткая информация о Pull Request."""

    pull_request_id: str = Field(..., description='Идентификатор PR')
    pull_request_name: str = Field(..., description='Название PR')
    author_id: str = Field(..., description='ID автора')
    status: str = Field(..., description='Статус PR (OPEN/MERGED)')

    class Config:
        from_attributes = True


class UserReviewsResponse(BaseModel):
    """Ответ со списком PR, где пользователь назначен ревьювером."""

    user_id: str = Field(..., description='Идентификатор пользователя')
    pull_requests: list[PullRequestShort] = Field(..., description='Список PR для ревью')
