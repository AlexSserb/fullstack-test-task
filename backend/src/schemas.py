"""Pydantic-схемы для сериализации и валидации данных API."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FileItem(BaseModel):
    """Полное представление загруженного файла для ответов API."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    original_name: str
    mime_type: str
    size: int
    processing_status: str
    scan_status: str | None
    scan_details: str | None
    metadata_json: dict | None
    requires_attention: bool
    created_at: datetime
    updated_at: datetime


class FileUpdate(BaseModel):
    """Данные для частичного обновления файла."""

    title: str


class AlertItem(BaseModel):
    """Представление оповещения для ответов API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    file_id: str
    level: str
    message: str
    created_at: datetime
