import logging
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.logging import structured_log

logger = logging.getLogger(__name__)


def add_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def handle_http_exception(request: Request, exc: HTTPException) -> JSONResponse:
        request_id = getattr(request.state, "request_id", str(uuid4()))
        logger.warning(
            structured_log(
                "http_exception",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                status_code=exc.status_code,
                detail=exc.detail,
            )
        )
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(RequestValidationError)
    async def handle_validation_exception(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        request_id = getattr(request.state, "request_id", str(uuid4()))
        logger.warning(
            structured_log(
                "request_validation_error",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                errors=exc.errors(),
            )
        )
        return JSONResponse(
            status_code=422,
            content={"detail": "Request validation error", "errors": exc.errors()},
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_exception(request: Request, exc: Exception) -> JSONResponse:
        request_id = getattr(request.state, "request_id", str(uuid4()))
        logger.exception(
            structured_log(
                "unexpected_error",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                error_type=type(exc).__name__,
            )
        )
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})
