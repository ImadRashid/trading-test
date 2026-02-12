# Option B: Telegram Bot + Provider API

Telegram bot that accepts `/note <text>`, stores notes in SQLite, and optionally pushes notes to Notion.

## Features
- `/note <text>` command
- Saves notes to SQLite
- Env-based configuration (no secrets in code)
- Optional Notion API push bonus
- Structured logging
- Layered architecture (bot, services, repositories, db, config)

## Architecture (brief)
- **Entrypoint**: `bot.py` (thin runner)
- **Bot application**: `app/bot/application.py` wires dependencies and handlers
- **Bot handlers**: `app/bot/handlers.py` handles `/start` and `/note`
- **Service layer**: `app/services/note_service.py` orchestrates note save + optional provider push
- **Provider client**: `app/services/notion_service.py` calls Notion API
- **Repository layer**: `app/repositories/note_repository.py` handles SQL writes
- **DB layer**: `app/db/database.py` manages SQLite connection/schema
- **Config**: `app/core/config.py` reads env variables
- **Logging**: `app/core/logging.py` provides setup and structured logging helper

## Project files
- `bot.py`
- `app/bot/application.py`
- `app/bot/handlers.py`
- `app/services/note_service.py`
- `app/services/notion_service.py`
- `app/repositories/note_repository.py`
- `app/db/database.py`
- `app/core/config.py`
- `app/core/logging.py`
- `requirements.txt`
- `.env.example`

## Env vars
- `TELEGRAM_BOT_TOKEN` (required)
- `DATABASE_URL` (optional, default: `notes.db`)
- `NOTION_API_KEY` (optional)
- `NOTION_DATABASE_ID` (optional)
- `LOG_LEVEL` (optional, default: `INFO`)
- `SERVICE_NAME` (optional, default: `telegram-note-bot`)

## Run locally

1. Create and activate a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:
```bash
python -m pip install -r requirements.txt
```

3. Configure environment:
```bash
export TELEGRAM_BOT_TOKEN="<your-bot-token>"
export DATABASE_URL="notes.db"
export LOG_LEVEL="INFO"
export SERVICE_NAME="telegram-note-bot"
# Optional Notion bonus
export NOTION_API_KEY="<notion-api-key>"
export NOTION_DATABASE_ID="<notion-db-id>"
```

4. Start the bot:
```bash
python bot.py
```

## Usage
In Telegram chat with your bot:
```text
/note Buy BTC if breakout confirms
```

Expected reply:
```text
Saved note #1.
```
(If Notion is configured and succeeds: `Saved note #1. Also pushed to Notion.`)

## Notes
- For Notion push to work, your Notion database should have a `Name` title property.
- Keep secrets in environment variables only.
