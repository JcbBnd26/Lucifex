# Chunk G — Lucifex Core Errors

> **Authorship note.** This chunk document was written by the coding agent (GitHub Copilot) rather than by the planning agent (PA), which is Claude (claude.ai). The PA was unavailable due to token limits, so for Chunk G the coding agent both planned and executed the work, then wrote this document after the fact. The format follows the established Chunk D / Chunk E / Chunk F template; the "What was actually done" section reflects real execution rather than a forward plan.

You are working in the Lucifex project repository. Chunks A–C established the foundation, folder scaffold, and Python environment. Chunk D scaffolded the database. Chunk E added the auth crypto primitives. Chunk F introduced typed application settings (`pydantic-settings` `Settings`, asyncpg-driver enforcement, frozen singleton, Alembic env rewired).

Chunk G adds the project's domain exception hierarchy at `lucifex.core.errors`. Every failure that originates inside the domain layer raises a subclass of `DomainError`. The eventual API translation layer will catch `DomainError` once at the boundary and convert it into the right HTTP response. Infrastructure errors (database driver, HTTP client, OS-level) deliberately stay outside this hierarchy and propagate distinctly.

This chunk is small on purpose: pure-Python data classes, no I/O, no new dependencies. The point is to lock in the contract before repositories, the auth service, and the API layer are written, so all of those can build on it without retrofitting.

When this chunk was finished, all gates were green: ruff clean, mypy strict Success on 28 source files, pytest **50 passed** (27 from F + 11 settings + 12 new errors tests). No database commands were run.

---

## Architectural decisions for this chunk

Locked in before execution:

1. **Single base class.** Every domain exception subclasses `DomainError`. The boundary layer can write `except DomainError` once and catch anything domain-originated; infrastructure errors are a different shape and a different concern.
2. **Shallow hierarchy.** Exactly one extra level under `AuthError` (`AuthenticationError`, `AuthorizationError`). Resist deeper trees until concrete pain forces them.
3. **`code` is `str | None`, not `Enum`.** Codes are stable identifiers that grow over time. A string maps cleanly to JSON, log fields, and i18n keys; an `Enum` would force every layer that touches an error to know every code.
4. **`default_code` per subclass.** A `ClassVar` on each subclass declares its default code. Subclasses don't need to override `__init__`. Callers can still pass `code=...` explicitly to override per-instance.
5. **`details` is a defensive read-only copy.** Accept any `Mapping`, store as `MappingProxyType(dict(input))`. Mutating the source dict after construction never changes the recorded details, and `err.details["x"] = ...` raises `TypeError`.
6. **No HTTP status, no logging hook, no correlation ID.** Errors are *data*. HTTP translation is the API layer's job. Log enrichment is the observability layer's job. Correlation IDs come from `structlog` context vars later. Keep this module pure.
7. **`core.ValidationError` deliberately shadows `pydantic.ValidationError`.** `core/` does not import pydantic. Pydantic validation lives at the boundary (config, future API request schemas). Inside `core/`, `ValidationError` is unambiguously the domain rule violation.
8. **Re-export from `lucifex.core`.** Callers write `from lucifex.core import NotFoundError`, not `from lucifex.core.errors import ...`. The submodule path stays, but the package surface is the canonical import path.

---

## Operation 1 — Create `backend/src/lucifex/core/errors.py`

Create a new file at `backend/src/lucifex/core/errors.py` with this exact content:

```python
"""Domain exception hierarchy for Lucifex.

Every failure that originates in the domain layer raises a subclass of
`DomainError`. The API translation layer (added in a later chunk) catches
`DomainError` once at the boundary and converts it into the right HTTP
response. Infrastructure errors (database driver errors, HTTP client
errors, OS-level errors) are NOT subclasses of `DomainError` — they
propagate distinctly so the boundary layer can handle them differently.

Naming note: this module defines a `ValidationError` that intentionally
shadows `pydantic.ValidationError`. Code in `core/` does not import
pydantic; pydantic validation lives in the configuration and (future) API
schema layers, where the pydantic name is in scope and unambiguous.

Errors are data-only. They do NOT log themselves, carry HTTP status, or
hold correlation IDs — those concerns belong to the observability and
API layers, not to the error class.
"""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import Any, ClassVar

# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------


class DomainError(Exception):
    """Base class for all domain-originated errors.

    Subclasses set `default_code` to a stable string identifier (e.g.
    ``"not_found"``) that downstream layers map to HTTP status, log
    fields, or i18n keys. Callers may override the code per-instance by
    passing ``code=`` explicitly.

    The ``details`` mapping carries structured context (which row, which
    field, which limit) for logs and HTTP error bodies. The instance
    holds a defensive read-only copy — passing a dict and then mutating
    it later does not change the recorded details.
    """

    default_code: ClassVar[str | None] = None

    def __init__(
        self,
        message: str = "",
        *,
        code: str | None = None,
        details: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message: str = message
        self.code: str | None = code if code is not None else self.default_code
        self.details: Mapping[str, Any] = MappingProxyType(dict(details) if details else {})

    def __str__(self) -> str:
        return self.message

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"message={self.message!r}, "
            f"code={self.code!r}, "
            f"details={dict(self.details)!r})"
        )


# ---------------------------------------------------------------------------
# Concrete subclasses
# ---------------------------------------------------------------------------


class NotFoundError(DomainError):
    """A required entity could not be found."""

    default_code: ClassVar[str | None] = "not_found"


class ConflictError(DomainError):
    """The operation conflicts with current state.

    Raised on uniqueness violations, optimistic-lock failures, and any
    other "you can't do that right now because of state" condition.
    """

    default_code: ClassVar[str | None] = "conflict"


class ValidationError(DomainError):
    """A domain rule was violated.

    Distinct from `pydantic.ValidationError`, which covers schema-level
    parsing failures at the boundary. This class is for rule violations
    discovered after parsing — e.g. "role must be one of {...}" or
    "session is past expiry".
    """

    default_code: ClassVar[str | None] = "validation_error"


class AuthError(DomainError):
    """Base class for authentication and authorization failures.

    Use the more specific subclasses where possible. Catching
    `AuthError` is appropriate when the boundary handles both cases
    identically.
    """

    default_code: ClassVar[str | None] = "auth_error"


class AuthenticationError(AuthError):
    """The caller failed to prove who they are.

    Wrong password, expired session, missing/invalid token.
    """

    default_code: ClassVar[str | None] = "authentication_failed"


class AuthorizationError(AuthError):
    """The caller is authenticated but not permitted to do this."""

    default_code: ClassVar[str | None] = "authorization_failed"


class RateLimitError(DomainError):
    """The caller has exceeded a rate limit and should retry later.

    The retry hint (e.g. ``retry_after_seconds``) is carried in
    ``details`` for now; if/when a typed field is justified by the
    middleware that consumes it, it will be promoted.
    """

    default_code: ClassVar[str | None] = "rate_limited"


__all__ = [
    "AuthError",
    "AuthenticationError",
    "AuthorizationError",
    "ConflictError",
    "DomainError",
    "NotFoundError",
    "RateLimitError",
    "ValidationError",
]
```

---

## Operation 2 — Replace `backend/src/lucifex/core/__init__.py`

The existing `core/__init__.py` is empty. Replace it with this content:

```python
"""Pure domain logic.

This package holds the rules of the system: services, validators, and
types that operate on data and return data. No HTTP, no database, no
external APIs. See `core/README.md`.
"""

from lucifex.core.errors import (
    AuthError,
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    DomainError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)

__all__ = [
    "AuthError",
    "AuthenticationError",
    "AuthorizationError",
    "ConflictError",
    "DomainError",
    "NotFoundError",
    "RateLimitError",
    "ValidationError",
]
```

This makes `from lucifex.core import NotFoundError` the canonical import path.

---

## Operation 3 — Append an "Errors" subsection to `backend/src/lucifex/core/README.md`

The existing prose stays. Append the following after the "Organization" section:

```markdown
## Errors

Every domain-originated failure raises a subclass of `DomainError` from `lucifex.core.errors`. Never raise bare `Exception` from `core/` or from layers that depend on it. The API translation layer catches `DomainError` once at the boundary and maps it to the right HTTP response; infrastructure errors (DB driver, HTTP client, OS) propagate distinctly.

Current hierarchy:

- `DomainError` — base.
  - `NotFoundError`, `ConflictError`, `ValidationError`, `RateLimitError`.
  - `AuthError` — `AuthenticationError`, `AuthorizationError`.

Each error carries an optional `code` (stable string identifier) and a read-only `details` mapping for structured context.
```

---

## Operation 4 — Create `backend/tests/unit/test_errors.py`

Create a new file at `backend/tests/unit/test_errors.py` with this exact content:

```python
"""Unit tests for `lucifex.core.errors`."""

from __future__ import annotations

import pytest

from lucifex.core.errors import (
    AuthError,
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    DomainError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)

pytestmark = pytest.mark.unit


_CONCRETE_SUBCLASSES = [
    NotFoundError,
    ConflictError,
    ValidationError,
    AuthError,
    AuthenticationError,
    AuthorizationError,
    RateLimitError,
]


def test_domain_error_is_exception() -> None:
    assert issubclass(DomainError, Exception)


def test_domain_error_default_init() -> None:
    err = DomainError()

    assert err.message == ""
    assert err.code is None
    assert dict(err.details) == {}
    assert str(err) == ""


def test_domain_error_with_message_and_code() -> None:
    err = DomainError("boom", code="custom_code", details={"hint": "value"})

    assert err.message == "boom"
    assert err.code == "custom_code"
    assert dict(err.details) == {"hint": "value"}
    assert str(err) == "boom"


def test_details_is_defensively_copied() -> None:
    source = {"id": "abc"}
    err = DomainError("nope", details=source)

    source["id"] = "MUTATED"

    assert dict(err.details) == {"id": "abc"}


def test_details_is_read_only() -> None:
    err = DomainError("nope", details={"id": "abc"})

    with pytest.raises(TypeError):
        err.details["id"] = "MUTATED"  # type: ignore[index]


def test_details_defaults_to_empty_mapping() -> None:
    err = DomainError("x")

    assert len(err.details) == 0
    assert dict(err.details) == {}


@pytest.mark.parametrize(
    ("cls", "expected_code"),
    [
        (NotFoundError, "not_found"),
        (ConflictError, "conflict"),
        (ValidationError, "validation_error"),
        (AuthError, "auth_error"),
        (AuthenticationError, "authentication_failed"),
        (AuthorizationError, "authorization_failed"),
        (RateLimitError, "rate_limited"),
    ],
)
def test_subclass_default_code_applied(cls: type[DomainError], expected_code: str) -> None:
    assert cls("msg").code == expected_code


def test_subclass_explicit_code_overrides_default() -> None:
    err = NotFoundError("missing", code="user_not_found")

    assert err.code == "user_not_found"


@pytest.mark.parametrize("cls", _CONCRETE_SUBCLASSES)
def test_all_subclasses_catchable_as_domain_error(cls: type[DomainError]) -> None:
    with pytest.raises(DomainError):
        raise cls("x")


def test_authentication_and_authorization_are_auth_errors() -> None:
    assert issubclass(AuthenticationError, AuthError)
    assert issubclass(AuthorizationError, AuthError)
    assert issubclass(AuthError, DomainError)


def test_repr_contains_class_name_code_and_details() -> None:
    err = NotFoundError("missing user", details={"id": "u-1"})
    rendered = repr(err)

    assert "NotFoundError" in rendered
    assert "missing user" in rendered
    assert "not_found" in rendered
    assert "u-1" in rendered
```

---

## Constraints

Do not create any of the following:

- Mappers from `DomainError` to HTTP responses (that's the API bootstrap chunk).
- Mappers from `DomainError` to log records or Sentry events (that's the observability chunk).
- Infrastructure error wrappers (e.g. `IntegrityError → ConflictError`) — those land in the repository chunk where they're actually thrown.
- A `core/values.py` (Email, Role, etc.) — separate chunk.
- Any new runtime dependency.
- Any new pyproject.toml change.

Do not run:

- `git` commands.
- `alembic` commands or any database commands.
- `pip install` (no dependency changes).

---

## What was actually done (record of execution)

For the planning agent's reference — these are the file operations Copilot performed in this session, in order:

1. **Created** `backend/src/lucifex/core/errors.py` (~145 lines) with `DomainError` base and 7 subclasses. Uses `MappingProxyType` over a defensive `dict(...)` copy for `details`, and a `ClassVar[str | None]` `default_code` slot on each subclass.
2. **Replaced** the empty `backend/src/lucifex/core/__init__.py` with re-exports of all 8 names plus a sorted `__all__`.
3. **Appended** the "Errors" subsection (hierarchy summary + boundary rule) to `backend/src/lucifex/core/README.md`. Existing prose untouched.
4. **Created** `backend/tests/unit/test_errors.py` (~125 lines, **12 tests**) covering: base inheritance, default init, message/code round-trip, defensive `details` copy, read-only `details` mutation rejection, empty-default `details`, parametrized default-code-per-subclass, explicit-code override, parametrized "all subclasses catchable as `DomainError`", auth subclass relationships, and repr sanity.
5. **Auto-fixed** import ordering (`I001`) in three files via `ruff check --fix`:
   - `src/lucifex/core/__init__.py` (cosmetic only — alphabetical order was already correct, ruff's import-block format differed).
   - `tests/unit/test_errors.py` (cosmetic).
   - `tests/unit/test_settings.py` (pre-existing from Chunk F; ruff format unified `pydantic` + `lucifex` import grouping).
6. **Ran** the verification pipeline. Results:
   - `ruff format .` → 4 files reformatted (cosmetic), 30 unchanged.
   - `ruff check .` → all checks passed.
   - `mypy src` → Success on **28 source files**, no issues found.
   - `pytest -q` → **50 passed in 18.25s**, exit 0. New `lucifex.core.errors` module reaches 100% line coverage.

Nothing was committed or pushed by Copilot. The operator owns `git add` / `git commit` / `git push`.

---

## When you are finished

Report back with:

1. Confirmation that `backend/src/lucifex/core/errors.py` exists with `DomainError` and all 7 subclasses.
2. Confirmation that `backend/src/lucifex/core/__init__.py` re-exports all 8 names with `__all__` set.
3. Confirmation that `backend/src/lucifex/core/README.md` has the "Errors" subsection.
4. Confirmation that `backend/tests/unit/test_errors.py` exists with 12 tests, all marked `pytest.mark.unit`.
5. Confirmation that `backend/pyproject.toml` was NOT modified (no new dependency).
6. Output of `ruff check .` (expect: clean).
7. Output of `mypy src` (expect: Success on 28 source files).
8. Output of `pytest -q` final line (expect: 50 passed).

---

## After Copilot finishes — operator instructions

**1. Eye-check the high-stakes files:**

- `backend/src/lucifex/core/errors.py` — read top to bottom. This is the contract every higher layer will throw and translate. Verify:
  - Each subclass declares its `default_code` ClassVar.
  - `details` is wrapped in `MappingProxyType` over a `dict(...)` copy.
  - No HTTP, logging, or correlation-ID concerns leaked in.
- `backend/src/lucifex/core/__init__.py` — confirm `__all__` order matches the imports.

**2. Verify imports work:**

```powershell
cd c:\Projects\Lucifex\backend
.\.venv\Scripts\python.exe -c "from lucifex.core import DomainError, NotFoundError, ConflictError, ValidationError, AuthError, AuthenticationError, AuthorizationError, RateLimitError; print('errors ok')"
```

Should print `errors ok`.

**3. Spot-check a real raise/catch:**

```powershell
.\.venv\Scripts\python.exe -c "from lucifex.core import NotFoundError, DomainError; \
try: \
    raise NotFoundError('user missing', details={'id': 'abc'}) \
except DomainError as e: \
    print(e.code, dict(e.details))"
```

Expect: `not_found {'id': 'abc'}`.

**4. Run lint, types, and tests:**

```powershell
ruff check .
mypy src
pytest -q
```

Expected: ruff clean, mypy Success on 28 files, **50 tests passed**.

**5. Stage and commit:**

```powershell
git add .
git commit -m "Chunk G — core errors: DomainError hierarchy with stable codes and read-only details, 12 unit tests"
git push
```

---

## Looking ahead

Chunk G leaves the project in a state where:

- Every layer downstream of `core/` has a single, stable contract for failure: subclass `DomainError`, attach a `code` and `details`.
- The (future) API boundary can be written as one `except DomainError` clause that maps `code` → HTTP status + JSON body.
- The (future) observability layer can attach `details` to log records / Sentry events without each call site doing it manually.

Likely next chunks (PA's call):

- **Chunk H — Logging / observability bootstrap.** Wire `settings.log_level` into `structlog`, set up a context-var carrier for request/correlation IDs, define the boundary translator that combines `DomainError.code` + `DomainError.details` into log fields. (Sentry DSN gets added to `Settings` here.)
- **Chunk I — `UserRepository` + `SessionRepository`.** First DB-touching code. Translates SQLAlchemy `IntegrityError` → `ConflictError`, missing rows → `NotFoundError`. Brings in the first integration tests against Postgres (testcontainers or local).
- **Chunk J — Auth service** (`core/auth/services.py`). `register_user`, `authenticate`, `create_session`, `revoke_session`, etc. Uses Chunk E primitives + Chunk I repositories + Chunk G errors.
- **Chunk K — API bootstrap.** FastAPI app factory, single `DomainError` exception handler, health endpoint. Last piece before real routes start landing.
