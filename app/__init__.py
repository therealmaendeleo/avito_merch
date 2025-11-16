from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.example import router as example_router


def include_routes(app: FastAPI) -> None:
    """Регистрация всех роутеров приложения."""
    app.include_router(auth_router)
    app.include_router(example_router)
