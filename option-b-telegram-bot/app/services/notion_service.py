import logging

import requests

from app.core.config import settings
from app.core.logging import structured_log

logger = logging.getLogger(__name__)


class NotionService:
    def push_note(self, note_text: str) -> bool:
        if not settings.notion_api_key or not settings.notion_database_id:
            return False

        payload = {
            "parent": {"database_id": settings.notion_database_id},
            "properties": {
                "Name": {
                    "title": [
                        {
                            "text": {
                                "content": note_text[:2000],
                            }
                        }
                    ]
                }
            },
        }
        headers = {
            "Authorization": f"Bearer {settings.notion_api_key}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(
                "https://api.notion.com/v1/pages",
                json=payload,
                headers=headers,
                timeout=10,
            )
            response.raise_for_status()
            return True
        except requests.RequestException as exc:
            logger.warning(
                structured_log(
                    "notion_push_failed",
                    error=str(exc),
                )
            )
            return False
