import os


class Settings:
    def __init__(self) -> None:
        self.database_url = os.getenv("DATABASE_URL", "webhooks.db")
        self.webhook_secret = os.getenv("WEBHOOK_SECRET", "change-me")
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.service_name = os.getenv("SERVICE_NAME", "webhook-receiver")


settings = Settings()
