from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.config import STORAGE_DIR
from src.database import get_session
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


@router.get("", response_model=list[FileItem])
async def list_files_view(session: AsyncSession = Depends(get_session)):
    return await list_files(session)


@router.post("", response_model=FileItem, status_code=201)
async def create_file_view(
    title: str = Form(...),
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
):
    file_item = await create_file(session, title=title, upload_file=file)
    scan_file_for_threats.delay(file_item.id)
    return file_item


@router.get("/{file_id}", response_model=FileItem)
async def get_file_view(file_id: str, session: AsyncSession = Depends(get_session)):
    return await get_file(session, file_id)


@router.patch("/{file_id}", response_model=FileItem)
async def update_file_view(
    file_id: str,
    payload: FileUpdate,
    session: AsyncSession = Depends(get_session),
):
    return await update_file(session, file_id=file_id, title=payload.title)


@router.get("/{file_id}/download")
async def download_file(file_id: str, session: AsyncSession = Depends(get_session)):
    file_item = await get_file(session, file_id)
    stored_path = STORAGE_DIR / file_item.stored_name
    if not stored_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Stored file not found"
        )
    return FileResponse(
        path=stored_path,
        media_type=file_item.mime_type,
        filename=file_item.original_name,
    )


@router.delete("/{file_id}", status_code=204)
async def delete_file_view(file_id: str, session: AsyncSession = Depends(get_session)):
    await delete_file(session, file_id)
