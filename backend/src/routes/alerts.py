from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.schemas import AlertItem
from src.services.file_service import list_alerts

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertItem])
async def list_alerts_view(session: AsyncSession = Depends(get_session)):
    return await list_alerts(session)
