from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from functools import lru_cache

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from src.config import get_settings


@lru_cache
def get_engine() -> AsyncEngine:
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
    return async_sessionmaker(get_engine(), expire_on_commit=False)


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_engine()
    yield
    await get_engine().dispose()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with get_session_maker()() as session:
        yield session
