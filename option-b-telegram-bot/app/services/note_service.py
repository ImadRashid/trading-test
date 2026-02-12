import logging
from datetime import datetime, timezone

from app.core.logging import structured_log
from app.repositories.note_repository import NoteRepository
from app.services.notion_service import NotionService

logger = logging.getLogger(__name__)


class NoteService:
    def __init__(self, note_repository: NoteRepository, notion_service: NotionService) -> None:
        self.note_repository = note_repository
        self.notion_service = notion_service

    def create_note(self, chat_id: int, text: str) -> tuple[int, bool]:
        created_at = datetime.now(timezone.utc).isoformat()
        note_id = self.note_repository.insert_note(
            chat_id=chat_id,
            note_text=text,
            created_at=created_at,
        )

        notion_pushed = self.notion_service.push_note(text)
        logger.info(
            structured_log(
                "note_saved",
                chat_id=chat_id,
                note_id=note_id,
                notion_pushed=notion_pushed,
            )
        )
        return note_id, notion_pushed
