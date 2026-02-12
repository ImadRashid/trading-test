import hashlib
import hmac
import json
import os
import sqlite3
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, Header, HTTPException, Request

DB_PATH = os.getenv("DATABASE_URL", "webhooks.db")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "change-me")

app = FastAPI(title="Webhook Receiver", version="1.0.0")


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS webhooks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                payload_hash TEXT NOT NULL UNIQUE,
                payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def canonical_payload(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def payload_hash(payload_json: str) -> str:
    return hashlib.sha256(payload_json.encode("utf-8")).hexdigest()


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/webhook")
async def webhook(request: Request, x_signature: str | None = Header(default=None)) -> dict[str, Any]:
    if not x_signature or not hmac.compare_digest(x_signature, WEBHOOK_SECRET):
        raise HTTPException(status_code=401, detail="Invalid signature")

    try:
        payload = await request.json()
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="Invalid JSON body") from exc

    normalized = canonical_payload(payload)
    digest = payload_hash(normalized)
    created_at = datetime.now(timezone.utc).isoformat()

    with get_db() as conn:
        try:
            cursor = conn.execute(
                """
                INSERT INTO webhooks (payload_hash, payload_json, created_at)
                VALUES (?, ?, ?)
                """,
                (digest, normalized, created_at),
            )
            conn.commit()
            return {
                "status": "stored",
                "duplicate": False,
                "record_id": cursor.lastrowid,
                "payload_hash": digest,
            }
        except sqlite3.IntegrityError:
            row = conn.execute(
                "SELECT id, created_at FROM webhooks WHERE payload_hash = ?",
                (digest,),
            ).fetchone()
            return {
                "status": "duplicate",
                "duplicate": True,
                "record_id": row["id"] if row else None,
                "payload_hash": digest,
            }
