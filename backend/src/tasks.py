"""Celery-задачи для асинхронной обработки файлов в фоновом режиме."""

import asyncio
import logging

from celery import Celery

from src.config import get_settings
from src.database import get_worker_session_maker
from src.services import scan_service

logger = logging.getLogger(__name__)

_settings = get_settings()
celery_app = Celery(
    "file_tasks",
    broker=_settings.redis_url,
    backend=_settings.redis_url,
)


@celery_app.task
def scan_file_for_threats(file_id: str) -> None:
    """Запускает проверку файла на угрозы и передаёт управление задаче извлечения метаданных."""
    logger.info("Starting threat scan for file %s", file_id)
    try:

        async def _run() -> None:
            async with get_worker_session_maker()() as session:
                await scan_service.scan_file(session, file_id)

        asyncio.run(_run())
    except Exception:
        logger.exception("Threat scan failed for file %s", file_id)
        return
    logger.info("Threat scan completed for file %s, queuing metadata extraction", file_id)
    extract_file_metadata.delay(file_id)


@celery_app.task
def extract_file_metadata(file_id: str) -> None:
    """Извлекает метаданные файла и передаёт управление задаче отправки оповещения."""
    logger.info("Starting metadata extraction for file %s", file_id)
    try:

        async def _run() -> None:
            async with get_worker_session_maker()() as session:
                await scan_service.extract_metadata(session, file_id)

        asyncio.run(_run())
    except Exception:
        logger.exception("Metadata extraction failed for file %s", file_id)
        return
    logger.info("Metadata extraction completed for file %s, queuing alert", file_id)
    send_file_alert.delay(file_id)


@celery_app.task
def send_file_alert(file_id: str) -> None:
    """Создаёт оповещение по результатам обработки файла."""
    logger.info("Sending alert for file %s", file_id)
    try:

        async def _run() -> None:
            async with get_worker_session_maker()() as session:
                await scan_service.send_alert(session, file_id)

        asyncio.run(_run())
    except Exception:
        logger.exception("Alert sending failed for file %s", file_id)
        return
    logger.info("Alert sent for file %s", file_id)
