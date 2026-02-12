# Option B: Telegram Bot + Provider API

Telegram bot that accepts `/note <text>`, stores notes in SQLite, and optionally pushes notes to Notion.

## Features
- `/note <text>` command
- Saves notes to SQLite
- Env-based configuration (no secrets in code)
- Optional Notion API push bonus

## Architecture (brief)
- **Bot layer**: `python-telegram-bot` in `bot.py` using polling
- **Persistence**: SQLite table `notes` with `id`, `chat_id`, `note_text`, `created_at`
- **Provider API (optional)**: If `NOTION_API_KEY` and `NOTION_DATABASE_ID` are set, notes are also sent to Notion API

## Project files
- `bot.py`
- `requirements.txt`
- `.env.example`

## Env vars
- `TELEGRAM_BOT_TOKEN` (required)
- `DATABASE_URL` (optional, default: `notes.db`)
- `NOTION_API_KEY` (optional)
- `NOTION_DATABASE_ID` (optional)

## Run locally

1. Create and activate a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
export TELEGRAM_BOT_TOKEN="<your-bot-token>"
export DATABASE_URL="notes.db"
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
