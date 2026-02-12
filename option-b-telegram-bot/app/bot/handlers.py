import logging

from telegram import Update
from telegram.ext import ContextTypes

from app.core.logging import structured_log
from app.services.note_service import NoteService

logger = logging.getLogger(__name__)


class BotHandlers:
    def __init__(self, note_service: NoteService) -> None:
        self.note_service = note_service

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not update.message:
            return
        await update.message.reply_text("Send /note <text> to store a note in SQLite.")

    async def note(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not update.message or not update.effective_chat:
            return

        text = " ".join(context.args).strip()
        if not text:
            await update.message.reply_text("Usage: /note <text>")
            return

        chat_id = int(update.effective_chat.id)
        note_id, notion_pushed = self.note_service.create_note(chat_id=chat_id, text=text)

        response = f"Saved note #{note_id}."
        if notion_pushed:
            response += " Also pushed to Notion."

        logger.info(
            structured_log(
                "note_command_handled",
                chat_id=chat_id,
                note_id=note_id,
            )
        )
        await update.message.reply_text(response)
