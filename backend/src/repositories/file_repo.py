"""Репозиторий для работы с файлами в базе данных."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import StoredFile


class FileRepository:
    """Инкапсулирует все операции с таблицей files."""

    def __init__(self, session: AsyncSession) -> None:
        """Инициализирует репозиторий с переданной сессией БД."""
        self.session = session

    async def list_all(self) -> list[StoredFile]:
        """Возвращает все файлы, отсортированные по дате загрузки (новые первыми)."""
        result = await self.session.execute(
            select(StoredFile).order_by(StoredFile.created_at.desc()),
        )
        return list(result.scalars().all())

    async def get_by_id(self, file_id: str) -> StoredFile | None:
        """Возвращает файл по идентификатору или None, если не найден."""
        return await self.session.get(StoredFile, file_id)

    async def save(self, file_item: StoredFile) -> StoredFile:
        """Сохраняет или обновляет файл и возвращает актуальное состояние из БД."""
        self.session.add(file_item)
        await self.session.commit()
        await self.session.refresh(file_item)
        return file_item

    async def delete(self, file_item: StoredFile) -> None:
        """Удаляет запись о файле из базы данных."""
        self.session.delete(file_item)
        await self.session.commit()
