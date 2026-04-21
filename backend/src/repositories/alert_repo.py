"""Репозиторий для работы с оповещениями в базе данных."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Alert


class AlertRepository:
    """Инкапсулирует все операции с таблицей alerts."""

    def __init__(self, session: AsyncSession) -> None:
        """Инициализирует репозиторий с переданной сессией БД."""
        self.session = session

    async def list_all(self) -> list[Alert]:
        """Возвращает все оповещения, отсортированные по дате создания (новые первыми)."""
        result = await self.session.execute(
            select(Alert).order_by(Alert.created_at.desc()),
        )
        return list(result.scalars().all())

    async def save(self, alert: Alert) -> Alert:
        """Сохраняет оповещение и возвращает актуальное состояние из БД."""
        self.session.add(alert)
        await self.session.commit()
        await self.session.refresh(alert)
        return alert
