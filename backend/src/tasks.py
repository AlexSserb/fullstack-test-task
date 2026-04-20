"""Celery-задачи для асинхронной обработки файлов в фоновом режиме."""

import asyncio
from collections.abc import Coroutine
from typing import Any

from celery import Celery

from src.config import get_settings
from src.database import get_session_maker
from src.services import scan_service

_worker_loop: asyncio.AbstractEventLoop | None = None


def run_in_worker_loop(coroutine: Coroutine[Any, Any, None]) -> None:
    """Выполняет корутину в постоянном event loop воркера Celery."""
    global _worker_loop
    if _worker_loop is None or _worker_loop.is_closed():
        _worker_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_worker_loop)
    _worker_loop.run_until_complete(coroutine)


_settings = get_settings()
celery_app = Celery(
    "file_tasks",
    broker=_settings.redis_url,
    backend=_settings.redis_url,
)


@celery_app.task
def scan_file_for_threats(file_id: str) -> None:
    """Запускает проверку файла на угрозы и передаёт управление задаче извлечения метаданных."""

    async def _run() -> None:
        async with get_session_maker()() as session:
            await scan_service.scan_file(session, file_id)
        extract_file_metadata.delay(file_id)

    run_in_worker_loop(_run())


@celery_app.task
def extract_file_metadata(file_id: str) -> None:
    """Извлекает метаданные файла и передаёт управление задаче отправки оповещения."""

    async def _run() -> None:
        async with get_session_maker()() as session:
            await scan_service.extract_metadata(session, file_id)
        send_file_alert.delay(file_id)

    run_in_worker_loop(_run())


@celery_app.task
def send_file_alert(file_id: str) -> None:
    """Создаёт оповещение по результатам обработки файла."""

    async def _run() -> None:
        async with get_session_maker()() as session:
            await scan_service.send_alert(session, file_id)

    run_in_worker_loop(_run())
