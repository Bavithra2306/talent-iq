"""Turns exceptions into consistent JSON error responses.

Every error body has the same shape: ``{"detail": ..., "code": ..., "request_id": ...}``.
``HTTPException`` keeps its message; unexpected errors are logged with the
traceback and the client only sees a generic message plus the request id,
which can be searched for in the server logs.
"""

import logging

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.observability.logging import request_id_var

logger = logging.getLogger("talentiq.errors")


def _body(detail: object, code: str) -> dict[str, object]:
    body: dict[str, object] = {"detail": detail, "code": code}
    request_id = request_id_var.get()
    if request_id:
        body["request_id"] = request_id
    return body


async def http_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """``HTTPException`` raised by routes, handlers and dependencies."""
    assert isinstance(exc, StarletteHTTPException)
    return JSONResponse(
        status_code=exc.status_code,
        content=_body(exc.detail, f"http_{exc.status_code}"),
        headers=exc.headers,
    )


async def validation_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Request body / query validation errors (keeps FastAPI's field list)."""
    assert isinstance(exc, RequestValidationError)
    # Validator errors can carry exception objects, so stringify them.
    errors = jsonable_encoder(exc.errors(), custom_encoder={Exception: str})
    return JSONResponse(status_code=422, content=_body(errors, "validation_error"))


async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Anything unexpected: log the traceback, hide internals from the client."""
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content=_body("Something went wrong on our side. Please try again.", "internal_error"),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Registers all exception handlers on the app."""
    app.add_exception_handler(StarletteHTTPException, http_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(Exception, unhandled_error_handler)
