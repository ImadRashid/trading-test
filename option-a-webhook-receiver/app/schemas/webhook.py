from pydantic import BaseModel


class WebhookResponse(BaseModel):
    status: str
    duplicate: bool
    record_id: int | None
    payload_hash: str
