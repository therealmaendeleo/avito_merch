import functools
from abc import ABC

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings
from app.database.models import Base


# Декоратор для обработки сессии
def with_session(func):  # noqa
    @functools.wraps(func)
    async def wrapper(self, *args, **kwargs):  # noqa
        session = kwargs.get('session')
        if session is not None:
            return await func(self, *args, **kwargs)
        async with self.async_ses() as session:
            kwargs['session'] = session
            return await func(self, *args, **kwargs)

    return wrapper


# Декоратор для обработки сессии и коммита
def with_session_commit(func):  # noqa
    @functools.wraps(func)
    async def wrapper(self, *args, **kwargs):  # noqa
        session = kwargs.get('session')
        if session is not None:
            try:
                result = await func(self, *args, **kwargs)
                await session.commit()
                return result
            except Exception:
                await session.rollback()
                raise
        async with self.async_ses() as session:
            kwargs['session'] = session
            try:
                result = await func(self, *args, **kwargs)
                await session.commit()
                return result
            except Exception:
                await session.rollback()
                raise

    return wrapper


async_engine = create_async_engine(
    settings.PG_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_pre_ping=settings.DB_POOL_PRE_PING,
    echo=settings.DB_ECHO,
    connect_args={
        'command_timeout': settings.DB_COMMAND_TIMEOUT,
        'server_settings': {
            'statement_timeout': str(settings.DB_STATEMENT_TIMEOUT),
            'jit': 'off',
        },
    },
)

session_factory = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class BasePgInterface(ABC):  # noqa: B024
    def __init__(self) -> None:
        self.base = Base

    @property
    def engine(self) -> AsyncEngine:
        return async_engine

    def async_ses(self) -> AsyncSession:
        # выдаёт новую асинхронную сессию
        return session_factory()
