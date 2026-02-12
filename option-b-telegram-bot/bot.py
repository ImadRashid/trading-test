import logging
import os
import sqlite3
from datetime import datetime, timezone

import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

DB_PATH = os.getenv("DATABASE_URL", "notes.db")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
NOTION_API_KEY = os.getenv("NOTION_API_KEY", "")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID", "")

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
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


def save_note(chat_id: int, note_text: str) -> int:
    created_at = datetime.now(timezone.utc).isoformat()
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO notes (chat_id, note_text, created_at) VALUES (?, ?, ?)",
            (chat_id, note_text, created_at),
        )
        conn.commit()
        return int(cursor.lastrowid)


def push_to_notion(note_text: str) -> bool:
    if not NOTION_API_KEY or not NOTION_DATABASE_ID:
        return False

    payload = {
        "parent": {"database_id": NOTION_DATABASE_ID},
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
        "Authorization": f"Bearer {NOTION_API_KEY}",
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
        logger.warning("Notion push failed: %s", exc)
        return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Send /note <text> to store a note in SQLite."
    )


async def note(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    text = " ".join(context.args).strip()
    if not text:
        await update.message.reply_text("Usage: /note <text>")
        return

    chat_id = int(update.effective_chat.id)
    note_id = save_note(chat_id=chat_id, note_text=text)
    notion_pushed = push_to_notion(text)

    response = f"Saved note #{note_id}."
    if notion_pushed:
        response += " Also pushed to Notion."

    await update.message.reply_text(response)


def main() -> None:
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("Missing TELEGRAM_BOT_TOKEN environment variable")

    init_db()

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("note", note))

    logger.info("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
