import logging
import time
from uuid import uuid4

from fastapi import FastAPI, Request

from app.api.exception_handlers import add_exception_handlers
from app.api.routes import router
from app.core.config import settings
from app.core.logging import setup_logging, structured_log
from app.db.database import init_db

setup_logging(settings.log_level)
logger = logging.getLogger(__name__)

app = FastAPI(title="Webhook Receiver", version="1.0.0")
app.include_router(router)
add_exception_handlers(app)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or str(uuid4())
    request.state.request_id = request_id

    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start) * 1000, 2)

    response.headers["X-Request-ID"] = request_id
    logger.info(
        structured_log(
            "request_completed",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
        )
    )
    return response


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    logger.info(
        structured_log(
            "service_started",
            service_name=settings.service_name,
            database_url=settings.database_url,
        )
    )
