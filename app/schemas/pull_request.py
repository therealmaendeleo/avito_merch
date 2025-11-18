"""Схемы для работы с Pull Requests."""

from datetime import datetime

from pydantic import BaseModel, Field


class PullRequestCreateRequest(BaseModel):
    """Запрос на создание Pull Request."""

    pull_request_id: str = Field(..., description='Идентификатор PR')
    pull_request_name: str = Field(..., description='Название PR')
    author_id: str = Field(..., description='ID автора')


class PullRequestMergeRequest(BaseModel):
    """Запрос на merge Pull Request."""

    pull_request_id: str = Field(..., description='Идентификатор PR')


class PullRequestReassignRequest(BaseModel):
    """Запрос на переназначение ревьювера."""

    pull_request_id: str = Field(..., description='Идентификатор PR')
    old_user_id: str = Field(..., description='ID ревьювера для замены')


class PullRequestResponse(BaseModel):
    """Ответ с полной информацией о Pull Request."""

    pull_request_id: str = Field(..., description='Идентификатор PR')
    pull_request_name: str = Field(..., description='Название PR')
    author_id: str = Field(..., description='ID автора')
    status: str = Field(..., description='Статус PR (OPEN/MERGED)')
    assigned_reviewers: list[str] = Field(..., description='Список ID назначенных ревьюверов (0..2)')
    created_at: datetime | None = Field(None, alias='createdAt', description='Дата создания')
    merged_at: datetime | None = Field(None, alias='mergedAt', description='Дата merge')

    class Config:
        from_attributes = True
        populate_by_name = True


class PullRequestReassignResponse(BaseModel):
    """Ответ после переназначения ревьювера."""

    pr: PullRequestResponse = Field(..., description='Обновлённый PR')
    replaced_by: str = Field(..., description='ID нового ревьювера')
