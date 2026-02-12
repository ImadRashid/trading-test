import sqlite3

from app.core.config import settings


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(settings.database_url)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                note_text TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()
