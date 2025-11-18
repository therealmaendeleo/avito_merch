from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app import include_routes
from app.errors_handlers import register_errors_handlers

app = FastAPI()

register_errors_handlers(app)

include_routes(app)


def custom_openapi() -> dict[str, Any]:
    if app.openapi_schema:
        return app.openapi_schema

    # Стандартная схема
    openapi_schema = get_openapi(
        title='Avito Internship',
        version='1.0.0',
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi  # type: ignore
