"""Бизнес-логика для управления файлами: загрузка, чтение, обновление и удаление."""

import mimetypes
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import STORAGE_DIR
from src.models import Alert, ProcessingStatus, StoredFile
from src.repositories.alert_repo import AlertRepository
from src.repositories.file_repo import FileRepository


async def list_files(session: AsyncSession) -> list[StoredFile]:
    """Возвращает список всех загруженных файлов."""
    return await FileRepository(session).list_all()


async def list_alerts(session: AsyncSession) -> list[Alert]:
    """Возвращает список всех оповещений."""
    return await AlertRepository(session).list_all()


async def get_file(session: AsyncSession, file_id: str) -> StoredFile:
    """Возвращает файл по идентификатору или выбрасывает 404."""
    file_item = await FileRepository(session).get_by_id(file_id)
    if not file_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    return file_item


async def create_file(session: AsyncSession, title: str, upload_file: UploadFile) -> StoredFile:
    """Сохраняет загруженный файл на диск и создаёт запись в базе данных."""
    content = await upload_file.read()
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File is empty")

    file_id = str(uuid4())
    suffix = Path(upload_file.filename or "").suffix
    stored_name = f"{file_id}{suffix}"
    stored_path = STORAGE_DIR / stored_name
    stored_path.write_bytes(content)

    file_item = StoredFile(
        id=file_id,
        title=title,
        original_name=upload_file.filename or stored_name,
        stored_name=stored_name,
        mime_type=(upload_file.content_type or mimetypes.guess_type(stored_name)[0] or "application/octet-stream"),
        size=len(content),
        processing_status=ProcessingStatus.UPLOADED,
    )
    return await FileRepository(session).save(file_item)


async def update_file(session: AsyncSession, file_id: str, title: str) -> StoredFile:
    """Обновляет заголовок файла и возвращает обновлённую запись."""
    repo = FileRepository(session)
    file_item = await repo.get_by_id(file_id)
    if not file_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    file_item.title = title
    return await repo.save(file_item)


async def delete_file(session: AsyncSession, file_id: str) -> None:
    """Удаляет файл с диска и его запись из базы данных."""
    repo = FileRepository(session)
    file_item = await repo.get_by_id(file_id)
    if not file_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    stored_path = STORAGE_DIR / file_item.stored_name
    if stored_path.exists():
        stored_path.unlink()
    await repo.delete(file_item)
