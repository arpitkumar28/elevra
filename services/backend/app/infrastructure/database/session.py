"""Async database session factory."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

connect_args = {}
if settings.database_url_async.startswith("postgresql+asyncpg"):
    connect_args = {
        "connect_timeout": settings.db_connect_timeout,
        "ssl": settings.supabase_sslmode,
    }

engine = create_async_engine(
    settings.database_url_async,
    pool_pre_ping=True,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_timeout=settings.db_pool_timeout,
    connect_args=connect_args,
    echo=False,
)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
