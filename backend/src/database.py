"""Настройка подключения к базе данных."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from functools import lru_cache
from typing import Annotated

from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.config import get_settings


@lru_cache
def get_engine() -> AsyncEngine:
    """Создаёт и кеширует асинхронный движок SQLAlchemy с пулом соединений."""
    s = get_settings()
    return create_async_engine(
        s.database_url,
        pool_size=s.db_pool_size,
        max_overflow=s.db_max_overflow,
        pool_pre_ping=s.db_pool_pre_ping,
        pool_recycle=s.db_pool_recycle,
    )


@lru_cache
def get_session_maker() -> async_sessionmaker[AsyncSession]:
    """Создаёт и кеширует фабрику сессий на основе общего движка."""
    return async_sessionmaker(get_engine(), expire_on_commit=False)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    """Управляет жизненным циклом приложения: инициализирует и освобождает пул соединений."""
    get_engine()
    yield
    await get_engine().dispose()


async def get_session() -> AsyncGenerator[AsyncSession]:
    """FastAPI-зависимость: предоставляет сессию БД на время обработки запроса."""
    async with get_session_maker()() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]
