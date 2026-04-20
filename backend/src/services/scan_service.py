from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from src.config import STORAGE_DIR
from src.models import Alert, AlertLevel, ProcessingStatus, ScanStatus
from src.repositories.alert_repo import AlertRepository
from src.repositories.file_repo import FileRepository


async def scan_file(session: AsyncSession, file_id: str) -> None:
    repo = FileRepository(session)
    file_item = await repo.get_by_id(file_id)
    if not file_item:
        return

    file_item.processing_status = ProcessingStatus.PROCESSING
    reasons: list[str] = []
    extension = Path(file_item.original_name).suffix.lower()

    if extension in {".exe", ".bat", ".cmd", ".sh", ".js"}:
        reasons.append(f"suspicious extension {extension}")

    if file_item.size > 10 * 1024 * 1024:
        reasons.append("file is larger than 10 MB")

    if extension == ".pdf" and file_item.mime_type not in {
        "application/pdf",
        "application/octet-stream",
    }:
        reasons.append("pdf extension does not match mime type")

    file_item.scan_status = ScanStatus.SUSPICIOUS if reasons else ScanStatus.CLEAN
    file_item.scan_details = ", ".join(reasons) if reasons else "no threats found"
    file_item.requires_attention = bool(reasons)
    await repo.save(file_item)


async def extract_metadata(session: AsyncSession, file_id: str) -> None:
    repo = FileRepository(session)
    file_item = await repo.get_by_id(file_id)
    if not file_item:
        return

    stored_path = STORAGE_DIR / file_item.stored_name
    if not stored_path.exists():
        file_item.processing_status = ProcessingStatus.FAILED
        file_item.scan_status = file_item.scan_status or ScanStatus.FAILED
        file_item.scan_details = "stored file not found during metadata extraction"
        await repo.save(file_item)
        return

    metadata = {
        "extension": Path(file_item.original_name).suffix.lower(),
        "size_bytes": file_item.size,
        "mime_type": file_item.mime_type,
    }

    if file_item.mime_type.startswith("text/"):
        content = stored_path.read_text(encoding="utf-8", errors="ignore")
        metadata["line_count"] = len(content.splitlines())
        metadata["char_count"] = len(content)
    elif file_item.mime_type == "application/pdf":
        content = stored_path.read_bytes()
        metadata["approx_page_count"] = max(content.count(b"/Type /Page"), 1)

    file_item.metadata_json = metadata
    file_item.processing_status = ProcessingStatus.PROCESSED
    await repo.save(file_item)


async def send_alert(session: AsyncSession, file_id: str) -> None:
    file_item = await FileRepository(session).get_by_id(file_id)
    if not file_item:
        return

    if file_item.processing_status == ProcessingStatus.FAILED:
        alert = Alert(
            file_id=file_id, level=AlertLevel.CRITICAL, message="File processing failed"
        )
    elif file_item.requires_attention:
        alert = Alert(
            file_id=file_id,
            level=AlertLevel.WARNING,
            message=f"File requires attention: {file_item.scan_details}",
        )
    else:
        alert = Alert(
            file_id=file_id,
            level=AlertLevel.INFO,
            message="File processed successfully",
        )

    await AlertRepository(session).save(alert)
