from app.api.v1.router import router as v1_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.infrastructure.rate_limit.limiter import limiter
from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.middleware.cors import CORSMiddleware


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(
        title="Elevra API",
        version="0.1.0",
        docs_url="/docs" if settings.enable_docs else None,
        redoc_url="/redoc" if settings.enable_docs else None,
    )
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["authorization", "content-type", "x-request-id"],
    )
    app.include_router(v1_router, prefix="/api/v1")
    return app


app = create_app()
