from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from loguru import logger


def register_errors_handlers(app: FastAPI) -> None:
    @app.exception_handler(Exception)
    async def handle_internal_server_error(request: Request, exc: Exception) -> Response:
        logger.exception(f'Unhandled exception at {request.url}: {exc!r}')
        return JSONResponse(
            status_code=500,
            content={
                'code': 500,
                'detail': 'Непредвиденная ошибка',
            },
        )
