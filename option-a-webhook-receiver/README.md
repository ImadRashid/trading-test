# Option A: Webhook Receiver + DB

Small FastAPI service that receives webhooks, validates a shared secret header, stores payloads in SQLite, and prevents duplicate inserts using idempotency.

## Features
- `POST /webhook` endpoint
- Header validation with `X-Signature`
- SQLite persistence
- Idempotency via SHA-256 payload hash (`UNIQUE` in DB)
- Clean JSON responses
- `GET /health` endpoint
- Structured logs (request-level + business events)
- Centralized exception handling

## Architecture (brief)
- **Entrypoint**: `app/main.py` creates the FastAPI app and registers startup DB initialization.
- **Routes**: `app/api/routes.py` exposes `/health` and `/webhook`.
- **Service layer**: `app/services/webhook_service.py` handles payload normalization, hashing, and idempotent store logic.
- **Repository layer**: `app/repositories/webhook_repository.py` encapsulates SQL operations.
- **DB layer**: `app/db/database.py` manages SQLite connection and schema initialization.
- **Config**: `app/core/config.py` reads environment variables (`WEBHOOK_SECRET`, `DATABASE_URL`).
- **Logging**: `app/core/logging.py` provides logging setup and structured log formatting.
- **Global middleware**: request logging with latency and `X-Request-ID` response header.
- **Exception handling**: `app/api/exception_handlers.py` centralizes HTTP, validation, and unexpected error responses.
- **Schemas**: `app/schemas/webhook.py` defines response model.

## Project files
- `app.py` (thin compatibility entrypoint)
- `app/main.py`
- `app/api/routes.py`
- `app/services/webhook_service.py`
- `app/repositories/webhook_repository.py`
- `app/db/database.py`
- `app/core/config.py`
- `app/core/logging.py`
- `app/schemas/webhook.py`
- `app/api/exception_handlers.py`
- `requirements.txt`
- `.env.example`

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

3. Set environment variables:
```bash
export WEBHOOK_SECRET="super-secret"
export DATABASE_URL="webhooks.db"
export LOG_LEVEL="INFO"
```

4. Start server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Test requests

### 1) Valid request (stored)
```bash
curl -X POST http://127.0.0.1:8000/webhook \
  -H "Content-Type: application/json" \
  -H "X-Signature: super-secret" \
  -d '{"event":"trade.opened","order_id":"A123","amount":150}'
```

Example response:
```json
{
  "status": "stored",
  "duplicate": false,
  "record_id": 1,
  "payload_hash": "..."
}
```

### 2) Same payload again (duplicate)
Run the same curl command again.

Example response:
```json
{
  "status": "duplicate",
  "duplicate": true,
  "record_id": 1,
  "payload_hash": "..."
}
```

### 3) Invalid signature
```bash
curl -X POST http://127.0.0.1:8000/webhook \
  -H "Content-Type: application/json" \
  -H "X-Signature: wrong-secret" \
  -d '{"event":"trade.opened"}'
```

Returns `401` with:
```json
{"detail":"Invalid signature"}
```

## Deliverable notes
This project is ready to submit as:
- a GitHub repository link, or
- a zipped folder including this code and README.
