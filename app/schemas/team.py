from pydantic import BaseModel, Field


class TeamMember(BaseModel):
    """Схема участника команды."""

    user_id: str = Field(..., description='Идентификатор пользователя')
    username: str = Field(..., description='Имя пользователя')
    is_active: bool = Field(..., description='Флаг активности пользователя')


class TeamCreate(BaseModel):
    """Схема для создания команды."""

    team_name: str = Field(..., description='Уникальное имя команды')
    members: list[TeamMember] = Field(..., description='Список участников команды')


class TeamResponse(BaseModel):
    """Схема ответа с информацией о команде."""

    team_name: str = Field(..., description='Уникальное имя команды')
    members: list[TeamMember] = Field(..., description='Список участников команды')

    class Config:
        from_attributes = True
