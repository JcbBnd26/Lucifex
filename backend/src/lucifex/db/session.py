"""Async database engine and session factory for Lucifex.

Lucifex uses SQLAlchemy 2.x with the async engine (asyncpg driver). All
database access flows through this module — no module elsewhere in the
codebase should construct its own engine or session.

Usage in application code:

    from lucifex.db.session import get_session

    async with get_session() as session:
        result = await session.execute(...)

The engine and session factory are created lazily on first use. This lets
configuration load from environment variables before any database connection
is attempted.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Final

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

# ---------------------------------------------------------------------------
# Module-level singletons (initialized lazily)
# ---------------------------------------------------------------------------

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


# ---------------------------------------------------------------------------
# Engine and session factory
# ---------------------------------------------------------------------------


def init_engine(database_url: str, echo: bool = False) -> AsyncEngine:
    """Initialize the async engine and session factory.

    Called once at application startup with the database URL from settings.
    Subsequent calls reinitialize — useful for tests that need a clean slate.

    The `echo` flag enables SQL statement logging for debugging. Should be
    False in production, optionally True in development.
    """
    global _engine, _session_factory

    _engine = create_async_engine(
        database_url,
        echo=echo,
        future=True,
        # Connection pool tuning. Defaults are fine for a single-instance app;
        # revisit when running many workers.
        pool_pre_ping=True,
    )
    _session_factory = async_sessionmaker(
        _engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )
    return _engine


def get_engine() -> AsyncEngine:
    """Return the initialized async engine, or raise if not yet initialized."""
    if _engine is None:
        raise RuntimeError("Database engine not initialized. Call init_engine() first.")
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Return the initialized session factory, or raise if not yet initialized."""
    if _session_factory is None:
        raise RuntimeError("Session factory not initialized. Call init_engine() first.")
    return _session_factory


@asynccontextmanager
async def get_session() -> AsyncIterator[AsyncSession]:
    """Yield an async session inside a context manager.

    The session is committed on successful exit and rolled back on exception.
    Always closed when the context exits.

    Use this for one-shot operations. For request-scoped sessions in FastAPI,
    use a dependency that yields from this same factory.
    """
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------


async def close_engine() -> None:
    """Dispose the engine. Call at application shutdown."""
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
    _engine = None
    _session_factory = None


# ---------------------------------------------------------------------------
# Re-exported names
# ---------------------------------------------------------------------------

__all__: Final = [
    "close_engine",
    "get_engine",
    "get_session",
    "get_session_factory",
    "init_engine",
]
