import sqlite3
from typing import Any

from app.db.database import get_db


class WebhookRepository:
    def insert_webhook(self, payload_hash: str, payload_json: str, created_at: str) -> int:
        with get_db() as conn:
            cursor = conn.execute(
                """
                INSERT INTO webhooks (payload_hash, payload_json, created_at)
                VALUES (?, ?, ?)
                """,
                (payload_hash, payload_json, created_at),
            )
            conn.commit()
            return int(cursor.lastrowid)

    def get_by_hash(self, payload_hash: str) -> dict[str, Any] | None:
        with get_db() as conn:
            row = conn.execute(
                "SELECT id, created_at FROM webhooks WHERE payload_hash = ?",
                (payload_hash,),
            ).fetchone()
            return dict(row) if row else None

    @staticmethod
    def is_unique_violation(exc: sqlite3.IntegrityError) -> bool:
        return "UNIQUE constraint failed" in str(exc)
