import hmac
import json
import logging
from typing import Any

from fastapi import APIRouter, Header, HTTPException, Request

from app.core.config import settings
from app.core.logging import structured_log
from app.repositories.webhook_repository import WebhookRepository
from app.schemas.webhook import WebhookResponse
from app.services.webhook_service import WebhookService

router = APIRouter()
webhook_service = WebhookService(WebhookRepository())
logger = logging.getLogger(__name__)


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/webhook", response_model=WebhookResponse)
async def webhook(request: Request, x_signature: str | None = Header(default=None)) -> dict[str, Any]:
    request_id = getattr(request.state, "request_id", "unknown")

    if not x_signature or not hmac.compare_digest(x_signature, settings.webhook_secret):
        logger.warning(
            structured_log(
                "invalid_signature",
                request_id=request_id,
                path=request.url.path,
            )
        )
        raise HTTPException(status_code=401, detail="Invalid signature")

    try:
        payload = await request.json()
    except json.JSONDecodeError as exc:
        logger.warning(
            structured_log(
                "invalid_json_body",
                request_id=request_id,
                path=request.url.path,
            )
        )
        raise HTTPException(status_code=400, detail="Invalid JSON body") from exc

    return webhook_service.store_payload(payload=payload, request_id=request_id)
