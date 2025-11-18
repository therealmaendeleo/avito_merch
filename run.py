import os
import platform
import time

import uvicorn
from loguru import logger

if platform.system() != 'Windows':
    os.environ['TZ'] = 'Europe/Moscow'
    time.tzset()  # type: ignore[attr-defined]


def run_server() -> None:
    logger.info('swagger url http://localhost:8080/docs')
    uvicorn.run(
        app='app.main:app',
        host='0.0.0.0',  # noqa: S104
        port=8080,
    )


if __name__ == '__main__':
    run_server()
