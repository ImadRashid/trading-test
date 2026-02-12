import os


class Settings:
    def __init__(self) -> None:
        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.database_url = os.getenv("DATABASE_URL", "notes.db")
        self.notion_api_key = os.getenv("NOTION_API_KEY", "")
        self.notion_database_id = os.getenv("NOTION_DATABASE_ID", "")
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.service_name = os.getenv("SERVICE_NAME", "telegram-note-bot")


settings = Settings()
