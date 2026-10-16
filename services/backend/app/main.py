import logging
import time
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError

from app.api.v1.router import router as v1_router
from app.core.config import settings, validate_security_settings
from app.core.logging import configure_logging
from app.db.session import engine
from app.infrastructure.cache import cache_client

configure_logging()
logger = logging.getLogger("app.request")

validate_security_settings(settings)

@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info("service_starting environment=%s", settings.environment)
    yield
    cache_client.close()
    engine.dispose()
    logger.info("service_stopped environment=%s", settings.environment)


app = FastAPI(
    title="Elevra API",
    version="0.1.0",
    description="Foundational API for Elevra",
    lifespan=lifespan,
)

if "*" in settings.allowed_origins:
    raise RuntimeError("CORS_ORIGINS must list explicit origins when credentialed requests are enabled")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


def _normalize_error_code(detail: str) -> str:
    text = str(detail).lower()
    if "refresh token" in text:
        return "REFRESH_TOKEN_INVALID"
    if "invalid or expired token" in text:
        return "INVALID_OR_EXPIRED_TOKEN"
    if "invalid token" in text:
        return "INVALID_TOKEN"
    if "authentication" in text:
        return "AUTHENTICATION_FAILED"
    if "forbidden" in text or "admin access" in text:
        return "FORBIDDEN"
    if "rate limit" in text:
        return "RATE_LIMIT_EXCEEDED"
    if "email already" in text:
        return "EMAIL_ALREADY_REGISTERED"
    return "REQUEST_FAILED"


def _error_payload(code: str, message: str, request_id: str, detail: object | None = None) -> dict[str, object]:
    payload: dict[str, object] = {"error": {"code": code, "message": message, "request_id": request_id}}
    if detail is not None:
        payload["detail"] = detail
    return payload


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    request_id = getattr(request.state, "request_id", str(uuid4()))
    message = exc.detail if isinstance(exc.detail, str) else "Request failed"
    code = _normalize_error_code(message)
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_payload(code, message, request_id, message),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    request_id = getattr(request.state, "request_id", str(uuid4()))
    return JSONResponse(
        status_code=422,
        content=_error_payload("VALIDATION_ERROR", "Request validation failed", request_id, exc.errors()),
    )


@app.exception_handler(OperationalError)
async def database_operational_error_handler(request: Request, _exc: OperationalError):
    request_id = getattr(request.state, "request_id", str(uuid4()))
    return JSONResponse(
        status_code=503,
        content=_error_payload("DATABASE_UNAVAILABLE", "Database unavailable", request_id),
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, _exc: Exception):
    request_id = getattr(request.state, "request_id", str(uuid4()))
    logger.exception("Unhandled application error request_id=%s path=%s", request_id, request.url.path)
    return JSONResponse(
        status_code=500,
        content=_error_payload("INTERNAL_SERVER_ERROR", "An unexpected error occurred", request_id),
    )


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    request_id = request.headers.get("x-request-id", str(uuid4()))
    request.state.request_id = request_id
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start) * 1000, 2)
    response.headers["x-request-id"] = request_id
    # TLS is terminated by the platform/load balancer.  These headers make the
    # API safe to embed behind that boundary without relying on a browser
    # default.  HSTS is intentionally only emitted for HTTPS requests.
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    if request.url.scheme == "https" or request.headers.get("x-forwarded-proto") == "https":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    logger.info(
        "request_id=%s method=%s path=%s status_code=%s duration_ms=%s",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


app.include_router(v1_router, prefix="/api/v1")
