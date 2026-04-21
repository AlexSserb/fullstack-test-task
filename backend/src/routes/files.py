"""Роутер для управления файлами: загрузка, чтение, обновление, скачивание, удаление."""

from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from starlette import status

from src.config import STORAGE_DIR
from src.database import SessionDep
from src.schemas import FileItem, FileUpdate
from src.services.file_service import (
    create_file,
    delete_file,
    get_file,
    list_files,
    update_file,
)
from src.tasks import scan_file_for_threats

router = APIRouter(prefix="/files", tags=["files"])

TitleForm = Annotated[str, Form(...)]
FileUpload = Annotated[UploadFile, File(...)]


@router.get("", response_model=list[FileItem])
async def list_files_view(session: SessionDep) -> list[FileItem]:
    """Возвращает список всех загруженных файлов."""
    return await list_files(session)


@router.post("", response_model=FileItem, status_code=201)
async def create_file_view(
    session: SessionDep,
    title: TitleForm,
    file: FileUpload,
) -> FileItem:
    """Принимает файл, сохраняет его и запускает фоновую обработку."""
    file_item = await create_file(session, title=title, upload_file=file)
    scan_file_for_threats.delay(file_item.id)
    return file_item


@router.get("/{file_id}", response_model=FileItem)
async def get_file_view(file_id: str, session: SessionDep) -> FileItem:
    """Возвращает информацию о файле по его идентификатору."""
    return await get_file(session, file_id)


@router.patch("/{file_id}", response_model=FileItem)
async def update_file_view(file_id: str, payload: FileUpdate, session: SessionDep) -> FileItem:
    """Обновляет заголовок файла."""
    return await update_file(session, file_id=file_id, title=payload.title)


@router.get("/{file_id}/download")
async def download_file(file_id: str, session: SessionDep) -> FileResponse:
    """Возвращает содержимое файла для скачивания."""
    file_item = await get_file(session, file_id)
    stored_path = STORAGE_DIR / file_item.stored_name
    if not stored_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stored file not found",
        )
    return FileResponse(
        path=stored_path,
        media_type=file_item.mime_type,
        filename=file_item.original_name,
    )


@router.delete("/{file_id}", status_code=204)
async def delete_file_view(file_id: str, session: SessionDep) -> None:
    """Удаляет файл с диска и из базы данных."""
    await delete_file(session, file_id)
