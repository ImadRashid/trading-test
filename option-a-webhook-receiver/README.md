# Option A: Webhook Receiver + DB

Small FastAPI service that receives webhooks, validates a shared secret header, stores payloads in SQLite, and prevents duplicate inserts using idempotency.

## Features
- `POST /webhook` endpoint
- Header validation with `X-Signature`
- SQLite persistence
- Idempotency via SHA-256 payload hash (`UNIQUE` in DB)
- Clean JSON responses
- `GET /health` endpoint

## Architecture (brief)
- **API layer**: FastAPI in `app.py`
- **Validation**: `X-Signature` is compared with `WEBHOOK_SECRET` using constant-time `hmac.compare_digest`
- **Storage**: SQLite table `webhooks` with columns:
  - `id`
  - `payload_hash` (unique)
  - `payload_json`
  - `created_at`
- **Idempotency**: payload is canonicalized (stable JSON), hashed, and inserted. If hash already exists, response marks as duplicate and returns existing record info.

## Project files
- `app.py`
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
```

4. Start server:
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
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
