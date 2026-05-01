"""Alembic environment configuration.

This file is invoked by Alembic when running migrations. It connects
SQLAlchemy's declarative metadata to Alembic's autogenerate machinery and
loads the database URL from environment variables.

The async migration support comes from running migrations through an async
engine, which matches how the application connects in production.
"""

from __future__ import annotations

import asyncio
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# ---------------------------------------------------------------------------
# Import all models so their metadata is registered with Base.metadata
# ---------------------------------------------------------------------------
# Importing the models package triggers the registration block in
# `db/models/__init__.py`, which imports each model module. Without this
# line, Alembic autogenerate would see an empty metadata object.
# ---------------------------------------------------------------------------

from lucifex.db.base import Base
import lucifex.db.models  # noqa: F401  # registers all models

# ---------------------------------------------------------------------------
# Alembic config
# ---------------------------------------------------------------------------

config = context.config

# Configure Python logging from the alembic.ini [loggers] section.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata is what autogenerate compares the database to.
target_metadata = Base.metadata


# ---------------------------------------------------------------------------
# Database URL from environment
# ---------------------------------------------------------------------------


def get_database_url() -> str:
    """Read the database URL from environment.

    Required: LUCIFEX_DATABASE_URL.

    Expected format: postgresql+asyncpg://user:pass@host:port/dbname

    The +asyncpg driver is required because the application uses async
    sessions throughout. Migrations run through the same async engine to
    match production connection behavior.
    """
    url = os.getenv("LUCIFEX_DATABASE_URL")
    if not url:
        raise RuntimeError(
            "LUCIFEX_DATABASE_URL is not set. Configure it in your "
            "environment or .env file before running migrations."
        )
    return url


# ---------------------------------------------------------------------------
# Migration runners
# ---------------------------------------------------------------------------


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    Generates SQL without connecting to a database. Useful for review or
    for emitting SQL to apply manually in restricted environments.
    """
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """The actual migration logic, called from inside an async connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode against a real database connection."""
    section = config.get_section(config.config_ini_section, {})
    section["sqlalchemy.url"] = get_database_url()

    connectable = async_engine_from_config(
        section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
