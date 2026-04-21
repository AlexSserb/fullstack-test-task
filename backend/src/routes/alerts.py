"""Роутер для работы с оповещениями."""

from fastapi import APIRouter

from src.database import SessionDep
from src.schemas import AlertItem
from src.services.file_service import list_alerts

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertItem])
async def list_alerts_view(session: SessionDep) -> list[AlertItem]:
    """Возвращает список всех оповещений, отсортированных по дате создания."""
    return await list_alerts(session)
