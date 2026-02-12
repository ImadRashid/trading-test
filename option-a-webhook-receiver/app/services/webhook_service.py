import hashlib
import json
import logging
import sqlite3
from datetime import datetime, timezone
from typing import Any

from app.core.logging import structured_log
from app.repositories.webhook_repository import WebhookRepository

logger = logging.getLogger(__name__)


class WebhookService:
    def __init__(self, repository: WebhookRepository) -> None:
        self.repository = repository

    @staticmethod
    def canonical_payload(payload: Any) -> str:
        return json.dumps(payload, sort_keys=True, separators=(",", ":"))

    @staticmethod
    def payload_hash(payload_json: str) -> str:
        return hashlib.sha256(payload_json.encode("utf-8")).hexdigest()

    def store_payload(self, payload: Any, request_id: str) -> dict[str, Any]:
        normalized = self.canonical_payload(payload)
        digest = self.payload_hash(normalized)
        created_at = datetime.now(timezone.utc).isoformat()

        try:
            record_id = self.repository.insert_webhook(
                payload_hash=digest,
                payload_json=normalized,
                created_at=created_at,
            )
            logger.info(
                structured_log(
                    "webhook_stored",
                    request_id=request_id,
                    payload_hash=digest,
                    record_id=record_id,
                )
            )
            return {
                "status": "stored",
                "duplicate": False,
                "record_id": record_id,
                "payload_hash": digest,
            }
        except sqlite3.IntegrityError as exc:
            if not self.repository.is_unique_violation(exc):
                raise

            existing = self.repository.get_by_hash(digest)
            record_id = existing["id"] if existing else None
            logger.info(
                structured_log(
                    "webhook_duplicate",
                    request_id=request_id,
                    payload_hash=digest,
                    record_id=record_id,
                )
            )
            return {
                "status": "duplicate",
                "duplicate": True,
                "record_id": record_id,
                "payload_hash": digest,
            }
