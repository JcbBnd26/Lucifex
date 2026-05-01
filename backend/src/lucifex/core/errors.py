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
        self.details: Mapping[str, Any] = MappingProxyType(
            dict(details) if details else {}
        )

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
