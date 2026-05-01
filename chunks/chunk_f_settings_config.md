# Chunk F — Lucifex Settings & Config

> **Authorship note.** This chunk document was written by the coding agent (GitHub Copilot) rather than by the planning agent (claude.ai). The PA was unavailable due to token limits, so for Chunk F the coding agent both planned and executed the work, then wrote this document after the fact. As a result, the format follows the established Chunk D / Chunk E template but the "What was actually done" section reflects real execution rather than a forward plan.

You are working in the Lucifex project repository. Chunks A–C established the foundation, folder scaffold, and Python environment. Chunk D scaffolded the database (declarative base, mixins, async session, `users` + `sessions` models, first Alembic migration). Chunk E added the auth crypto primitives (`hash_password`, `verify_password`, `needs_rehash`, `generate_session_token`, `hash_session_token`, `constant_time_compare`) and the project's first real unit tests.

Chunk F introduces a typed application settings layer. All `LUCIFEX_*` environment variables are now loaded once into a single immutable `Settings` instance (via `pydantic-settings`), validated at load time. The Alembic environment was rewired to use this same settings object, so there is now exactly one place in the codebase that reads environment variables.

This chunk is deliberately narrow in scope: only app-wide infrastructure settings (database URL, encryption key, environment name, log level). Per-feature secrets — provider API keys, OAuth client IDs, Sentry DSN, queue/worker config, CORS origins — are explicitly **out of scope** and are added in the chunks that introduce those features.

When this chunk was finished, all gates were green: ruff clean, mypy strict Success on 27 source files, pytest 27 passed (16 from Chunk E + 11 new). No database commands were run.

---

## Architectural decisions for this chunk

Locked in before execution:

1. **Single source of configuration.** All `LUCIFEX_*` env vars are read in exactly one place: `lucifex.config.settings.Settings`. No module elsewhere calls `os.environ.get(...)` for app settings.
2. **`pydantic-settings`, not bespoke parsing.** The dependency was already declared in Chunk A. We use it instead of hand-rolling env parsing or wrapping `os.environ` in helpers.
3. **Validate at load time, fail loudly.** Missing required vars, wrong DB driver, too-short keys, and invalid literal values surface as `ValidationError` at startup — not as a `KeyError` or runtime error later.
4. **Frozen settings.** `model_config = SettingsConfigDict(frozen=True)`. Mutating a settings instance after load is a bug; freezing makes it impossible.
5. **Cached singleton.** `get_settings()` is wrapped in `functools.lru_cache(maxsize=1)`. Tests call `get_settings.cache_clear()` between cases.
6. **Driver enforcement.** A `field_validator` on `database_url` rejects any scheme other than `postgresql+asyncpg`. The application is async-only; a sync driver silently breaks at the first `await`.
7. **Secrets typed as `SecretStr`.** The encryption key is wrapped to prevent accidental leakage via `repr()` or log dumps.
8. **Narrow scope.** Only four fields. Feature flags, provider keys, Sentry DSN, etc. are deferred to feature-introduction chunks.
9. **No new runtime dependency.** `pydantic-settings>=2.6,<3.0` was already in the Chunk A dependency list.

---

## Operation 1 — Create `backend/src/lucifex/config/settings.py`

Create a new file at `backend/src/lucifex/config/settings.py` with this exact content:

```python
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
```

Notes on the `# type: ignore[call-arg]` on `Settings()`:
- `pydantic-settings` populates required fields from environment variables, but the type checker can't see that and would otherwise flag the no-arg call as missing required arguments.
- This is the standard pattern from the `pydantic-settings` docs.

---

## Operation 2 — Update `backend/src/lucifex/config/__init__.py`

Replace the contents of `backend/src/lucifex/config/__init__.py` (previously empty) with this exact content:

```python
"""Typed application configuration.

See `lucifex.config.settings.Settings` for the full list of supported
environment variables. Use `get_settings()` to retrieve the cached
instance.
"""

from lucifex.config.settings import Settings, get_settings

__all__ = ["Settings", "get_settings"]
```

---

## Operation 3 — Wire the Alembic env to typed settings

Edit `backend/src/lucifex/db/migrations/env.py`. Two changes:

**3a.** Remove `import os` from the module imports and add `from lucifex.config import get_settings` to the model-import block. The top of the file should read:

```python
from __future__ import annotations

import asyncio
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

from lucifex.config import get_settings
from lucifex.db.base import Base
import lucifex.db.models  # noqa: F401  # registers all models
```

**3b.** Replace the `get_database_url()` function body with a delegation to `get_settings()`. The function becomes:

```python
def get_database_url() -> str:
    """Return the database URL from typed settings.

    Delegates to `lucifex.config.get_settings()`. A missing
    `LUCIFEX_DATABASE_URL`, an invalid driver, or any other configuration
    error surfaces here as a `pydantic.ValidationError`, before Alembic
    attempts a connection.

    The +asyncpg driver is required because the application uses async
    sessions throughout. Migrations run through the same async engine to
    match production connection behavior.
    """
    return str(get_settings().database_url)
```

The behavior is observably identical for the operator (a missing env still aborts startup) but the validation now also catches a wrong driver and a too-short encryption key, and reuses the same code path that the rest of the application uses.

The rest of `env.py` (offline runner, online runner, async engine setup) is unchanged.

---

## Operation 4 — Append a "Current settings" section to `backend/src/lucifex/config/README.md`

The existing prose stays. Append the following after the "Local development" section:

```markdown
## Current settings

All variables use the `LUCIFEX_` prefix. See `.env.example` at the repo root for the canonical list and example values.

| Field | Env var | Type | Default | Notes |
|---|---|---|---|---|
| `database_url` | `LUCIFEX_DATABASE_URL` | `PostgresDsn` | required | Must use the `postgresql+asyncpg` driver. |
| `encryption_key` | `LUCIFEX_ENCRYPTION_KEY` | `SecretStr` | required | Minimum 32 characters. Generate with `secrets.token_urlsafe(32)`. |
| `env` | `LUCIFEX_ENV` | `Literal["development", "staging", "production"]` | `development` | |
| `log_level` | `LUCIFEX_LOG_LEVEL` | `Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]` | `INFO` | Stored only — wired into `structlog` in a later chunk. |

Use `get_settings()` (cached) to retrieve the singleton:

\`\`\`python
from lucifex.config import get_settings

settings = get_settings()
print(settings.env)
\`\`\`

Settings instances are frozen — assignment after load raises.
```

(In the actual README, the inner code fence uses real triple-backticks; the escapes above are only because this chunk doc is itself a markdown file.)

---

## Operation 5 — Create `backend/tests/unit/test_settings.py`

Create a new file at `backend/tests/unit/test_settings.py` with this exact content:

```python
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
    monkeypatch.setenv(
        "LUCIFEX_DATABASE_URL", "postgresql://user:pass@localhost:5432/lucifex_test"
    )
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
```

The `(ValidationError, CoreValidationError, TypeError, AttributeError)` tuple in `test_settings_is_frozen` is intentional. Pydantic v2 raises `ValidationError` from its core when a frozen model is mutated, but the exact exception class can shift between minor versions and runtime conditions — accepting any of the four common shapes makes the test resilient without weakening the assertion.

---

## Constraints

Do not create any of the following:

- A `feature_flags.py` (deferred until the first real feature flag is needed).
- A logging configuration module (`log_level` is stored but not yet wired into `structlog`; that's an observability-chunk concern).
- An `errors.py` exception hierarchy (planned for Chunk G).
- Any new runtime dependency. `pydantic-settings` was already added in Chunk A.
- A real `.env` file. `.env.example` already exists (created in Chunk D).

Do not touch:

- `backend/pyproject.toml` (no dependency changes).
- `.env.example` (the four variables it documents are already correct).
- Any model, migration, or auth file.
- Any frontend or CI file.

Do not run:

- Any `alembic` command.
- Any database commands.
- Any git commands.

---

## What was actually done (record of execution)

For the planning agent's reference — these are the file operations Copilot performed in this session, in order:

1. **Created** `backend/src/lucifex/config/settings.py` (122 lines) with the `Settings` class, two field validators, and the cached `get_settings()` accessor.
2. **Replaced** the empty `backend/src/lucifex/config/__init__.py` with a re-export of `Settings` and `get_settings`.
3. **Edited** `backend/src/lucifex/db/migrations/env.py`:
   - Removed `import os`.
   - Added `from lucifex.config import get_settings`.
   - Replaced the body of `get_database_url()` with `return str(get_settings().database_url)`.
4. **Appended** a "Current settings" subsection (table + example) to `backend/src/lucifex/config/README.md`. Existing prose was untouched.
5. **Created** `backend/tests/unit/test_settings.py` (135 lines, 11 tests) covering env loading, driver enforcement, key length, defaults, invalid literals, missing required vars, caching, and frozen-mutation rejection.
6. **Auto-fixed** import ordering (`I001`) in two pre-existing test files (`tests/unit/test_passwords.py`, `tests/unit/test_tokens.py`) via `ruff check --fix`. These were unrelated cosmetic touches that ruff flagged after a `ruff format` pass — no semantic change.
7. **Ran** the full verification pipeline. Results:
   - `ruff format .` → 9 files reformatted (mostly cosmetic line-ending / blank-line normalization), 23 unchanged.
   - `ruff check .` → all checks passed.
   - `mypy src` → Success on **27 source files**, no issues found. (Note: `mypy` reports `pyproject.toml: note: unused section(s): module = ['arq.*']` — this override is still there for future use and is harmless.)
   - `pytest -q` → **27 passed in 22.02s**, exit 0. Coverage of the new `lucifex.config` package is 100%.

Nothing was committed or pushed by Copilot. The operator owns `git add` / `git commit` / `git push` for this chunk.

---

## When you are finished

Report back with:

1. Confirmation that `backend/src/lucifex/config/settings.py` exists with `Settings`, `get_settings`, and both field validators.
2. Confirmation that `backend/src/lucifex/config/__init__.py` re-exports `Settings` and `get_settings` with `__all__` set.
3. Confirmation that `backend/src/lucifex/db/migrations/env.py` no longer imports `os`, imports `get_settings` from `lucifex.config`, and that `get_database_url()` delegates to it.
4. Confirmation that `backend/src/lucifex/config/README.md` has the "Current settings" section.
5. Confirmation that `backend/tests/unit/test_settings.py` exists with 11 tests, all marked `pytest.mark.unit`.
6. Confirmation that no new dependency was added to `pyproject.toml`.
7. Output of `ruff check .` (expect: clean).
8. Output of `mypy src` (expect: Success on 27 source files).
9. Output of `pytest -q` final line (expect: 27 passed).
10. The file tree of `backend/src/lucifex/config/` after the chunk.

---

## After Copilot finishes — operator instructions

**1. Eye-check the high-stakes file:**

- `backend/src/lucifex/config/settings.py` — read top to bottom. This is the only place the application reads environment variables. Verify both validators do what the docstrings say.
- `backend/src/lucifex/db/migrations/env.py` — confirm `os` is gone, `get_settings` is imported, and `get_database_url()` is a one-liner.

**2. Verify imports work** (with the venv active and required env vars set):

```powershell
$env:LUCIFEX_DATABASE_URL = "postgresql+asyncpg://lucifex:lucifex@localhost:5432/lucifex_dev"
$env:LUCIFEX_ENCRYPTION_KEY = "x" * 40

python -c "from lucifex.config import Settings, get_settings; s = get_settings(); print('config ok', s.env, s.log_level)"
python -c "from lucifex.db.migrations.env import get_database_url; print('migrations ok', get_database_url())"
```

Both should print without error. The migrations import will print the asyncpg URL, confirming the wiring.

**3. Verify the negative paths:**

```powershell
Remove-Item Env:LUCIFEX_DATABASE_URL
python -c "from lucifex.config import Settings; Settings()"
```

This should raise `pydantic.ValidationError` mentioning `database_url` (and `encryption_key` if you also clear that). Restore the env vars after.

**4. Run lint, types, and tests:**

```powershell
ruff check .
mypy src
pytest -q
```

Expected: ruff clean, mypy Success on 27 files, 27 tests passed.

**5. Stage and commit:**

```powershell
git add .
git commit -m "Chunk F — typed settings: pydantic-settings Settings class, asyncpg driver enforcement, frozen singleton, migrations rewired, 11 unit tests"
git push
```

**6. (Optional) Smoke-check the migration still works against your local Postgres:**

If you have `lucifex_dev` set up from Chunk D, with `.env` populated:

```powershell
cd backend
alembic current
```

Should print the revision (`a1b2c3d4e5f6` if you previously ran `alembic upgrade head`) without error. The fact that this still works confirms the env-rewire didn't break anything.

---

## Looking ahead

Chunk F leaves the project in a state where:

- All four `LUCIFEX_*` env vars have one typed home.
- The Alembic env reads from that home, not directly from `os.environ`.
- The first feature-introduction chunks (Chunk G onward) can extend `Settings` with new fields as features are added — adding a field is one line, plus an env-var entry in `.env.example`, plus a test.

Likely next chunks:

- **Chunk G — Core errors** (`core/errors.py`): pure-Python exception hierarchy (`DomainError`, `NotFoundError`, `AuthError`, `ValidationError`). No I/O, no deps. Sets the contract for repository and service layers to come.
- **Chunk H — Logging / observability bootstrap**: wire `settings.log_level` into `structlog`, add request-ID middleware contract, set up Sentry init (DSN added to settings then).
- **Chunk I — Repositories**: `UserRepository`, `SessionRepository` with the first integration tests against a real (or testcontainers) Postgres.
