"""Pure domain logic.

This package holds the rules of the system: services, validators, and
types that operate on data and return data. No HTTP, no database, no
external APIs. See `core/README.md`.
"""

from lucifex.core.errors import (
    AuthenticationError,
    AuthError,
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
