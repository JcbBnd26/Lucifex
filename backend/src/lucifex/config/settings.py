"""Typed application settings loaded from environment variables.

All `LUCIFEX_*` environment variables are loaded once at startup into a
single immutable `Settings` instance. Code that needs configuration calls
`get_settings()` rather than reading `os.environ` directly.

Validation happens on load. A missing required variable, a malformed
database URL, or an invalid log level surfaces as a `ValidationError` at
startup — not as a `KeyError` at 3am when something tries to use it.

Scope of this module is deliberately narrow: it carries only app-wide
infrastructure settings (database URL, encryption key, environment name,
log level). Per-feature secrets (provider API keys, OAuth client IDs,
Sentry DSN) are added in the chunks that introduce those features.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Final, Literal

from pydantic import PostgresDsn, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Minimum acceptable length for the symmetric encryption key. The .env.example
# instructs operators to generate it with `secrets.token_urlsafe(32)`, which
# yields ~43 characters. We accept anything ≥ 32 to allow operators to use a
# different generator without changing this constant.
_MIN_ENCRYPTION_KEY_LENGTH: Final = 32


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    All fields are populated from environment variables with the prefix
    ``LUCIFEX_`` (e.g. ``database_url`` ← ``LUCIFEX_DATABASE_URL``). For
    local development a ``.env`` file at the repository root is also read.

    Settings are frozen after construction. Mutating a field raises.
    """

    model_config = SettingsConfigDict(
        env_prefix="LUCIFEX_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        frozen=True,
    )

    database_url: PostgresDsn
    encryption_key: SecretStr
    env: Literal["development", "staging", "production"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    @field_validator("database_url")
    @classmethod
    def _require_asyncpg_driver(cls, value: PostgresDsn) -> PostgresDsn:
        """Reject database URLs that don't use the asyncpg driver.

        The application uses async SQLAlchemy throughout. A plain
        ``postgresql://`` URL silently falls back to a sync driver and
        breaks at the first ``await`` — fail fast at load time instead.
        """
        if value.scheme != "postgresql+asyncpg":
            raise ValueError(
                "LUCIFEX_DATABASE_URL must use the postgresql+asyncpg driver "
                f"(got scheme {value.scheme!r}). The application connects "
                "asynchronously and the sync psycopg driver is not supported."
            )
        return value

    @field_validator("encryption_key")
    @classmethod
    def _require_minimum_key_length(cls, value: SecretStr) -> SecretStr:
        """Reject obviously-too-short encryption keys.

        Does not enforce entropy — that's the operator's responsibility.
        Just catches placeholder values and accidental truncation.
        """
        if len(value.get_secret_value()) < _MIN_ENCRYPTION_KEY_LENGTH:
            raise ValueError(
                "LUCIFEX_ENCRYPTION_KEY must be at least "
                f"{_MIN_ENCRYPTION_KEY_LENGTH} characters. Generate a real "
                'key with `python -c "import secrets; '
                'print(secrets.token_urlsafe(32))"`.'
            )
        return value


# ---------------------------------------------------------------------------
# Cached accessor
# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the process-wide `Settings` singleton.

    Result is cached so settings load once per process. Tests that
    manipulate environment variables must call ``get_settings.cache_clear()``
    before constructing fresh settings.
    """
    return Settings()  # type: ignore[call-arg]


__all__ = ["Settings", "get_settings"]
