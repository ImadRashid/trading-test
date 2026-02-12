import logging

from telegram.ext import ApplicationBuilder, CommandHandler

from app.bot.handlers import BotHandlers
from app.core.config import settings
from app.core.logging import setup_logging, structured_log
from app.db.database import init_db
from app.repositories.note_repository import NoteRepository
from app.services.note_service import NoteService
from app.services.notion_service import NotionService

logger = logging.getLogger(__name__)


def run_bot() -> None:
    setup_logging(settings.log_level)

    if not settings.telegram_bot_token:
        raise RuntimeError("Missing TELEGRAM_BOT_TOKEN environment variable")

    init_db()

    note_service = NoteService(
        note_repository=NoteRepository(),
        notion_service=NotionService(),
    )
    handlers = BotHandlers(note_service=note_service)

    application = ApplicationBuilder().token(settings.telegram_bot_token).build()
    application.add_handler(CommandHandler("start", handlers.start))
    application.add_handler(CommandHandler("note", handlers.note))

    logger.info(
        structured_log(
            "bot_started",
            service_name=settings.service_name,
            database_url=settings.database_url,
        )
    )
    application.run_polling()
