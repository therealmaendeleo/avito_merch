from fastapi import FastAPI

from app.api.pull_request import router as pull_request_router
from app.api.team import router as team_router
from app.api.user import router as user_router


def include_routes(app: FastAPI) -> None:
    """Подключение всех роутеров к приложению."""
    app.include_router(team_router)
    app.include_router(user_router)
    app.include_router(pull_request_router)
