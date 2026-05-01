"""Unit tests for `lucifex.config.settings`.

Each test isolates environment state with `monkeypatch` and clears the
`get_settings` LRU cache so prior tests can't leak state.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from pydantic import ValidationError
from pydantic_core import ValidationError as CoreValidationError

from lucifex.config import Settings, get_settings

pytestmark = pytest.mark.unit


_VALID_DB_URL = "postgresql+asyncpg://user:pass@localhost:5432/lucifex_test"
_VALID_KEY = "x" * 40


@pytest.fixture(autouse=True)
def _clear_settings_cache_and_env(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Wipe LUCIFEX_* env vars and the get_settings cache before each test."""
    for name in (
        "LUCIFEX_DATABASE_URL",
        "LUCIFEX_ENCRYPTION_KEY",
        "LUCIFEX_ENV",
        "LUCIFEX_LOG_LEVEL",
    ):
        monkeypatch.delenv(name, raising=False)
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def _set_required_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LUCIFEX_DATABASE_URL", _VALID_DB_URL)
    monkeypatch.setenv("LUCIFEX_ENCRYPTION_KEY", _VALID_KEY)


def test_settings_loads_from_env_with_prefix(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LUCIFEX_DATABASE_URL", _VALID_DB_URL)
    monkeypatch.setenv("LUCIFEX_ENCRYPTION_KEY", _VALID_KEY)
    monkeypatch.setenv("LUCIFEX_ENV", "production")
    monkeypatch.setenv("LUCIFEX_LOG_LEVEL", "WARNING")

    settings = Settings()

    assert str(settings.database_url) == _VALID_DB_URL
    assert settings.encryption_key.get_secret_value() == _VALID_KEY
    assert settings.env == "production"
    assert settings.log_level == "WARNING"


def test_database_url_must_use_asyncpg_driver(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LUCIFEX_DATABASE_URL", "postgresql://user:pass@localhost:5432/lucifex_test")
    monkeypatch.setenv("LUCIFEX_ENCRYPTION_KEY", _VALID_KEY)

    with pytest.raises(ValidationError, match="asyncpg"):
        Settings()


def test_encryption_key_min_length(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LUCIFEX_DATABASE_URL", _VALID_DB_URL)
    monkeypatch.setenv("LUCIFEX_ENCRYPTION_KEY", "too-short")

    with pytest.raises(ValidationError, match="at least"):
        Settings()


def test_env_defaults_to_development(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_required_env(monkeypatch)
    assert Settings().env == "development"


def test_log_level_defaults_to_info(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_required_env(monkeypatch)
    assert Settings().log_level == "INFO"


def test_invalid_env_value_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_required_env(monkeypatch)
    monkeypatch.setenv("LUCIFEX_ENV", "banana")

    with pytest.raises(ValidationError):
        Settings()


def test_invalid_log_level_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_required_env(monkeypatch)
    monkeypatch.setenv("LUCIFEX_LOG_LEVEL", "loud")

    with pytest.raises(ValidationError):
        Settings()


def test_missing_database_url_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LUCIFEX_ENCRYPTION_KEY", _VALID_KEY)

    with pytest.raises(ValidationError, match="database_url"):
        Settings()


def test_missing_encryption_key_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LUCIFEX_DATABASE_URL", _VALID_DB_URL)

    with pytest.raises(ValidationError, match="encryption_key"):
        Settings()


def test_get_settings_is_cached(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_required_env(monkeypatch)

    first = get_settings()
    second = get_settings()
    assert first is second

    get_settings.cache_clear()
    third = get_settings()
    assert third is not first


def test_settings_is_frozen(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_required_env(monkeypatch)
    settings = Settings()

    with pytest.raises((ValidationError, CoreValidationError, TypeError, AttributeError)):
        settings.env = "production"  # type: ignore[misc]
