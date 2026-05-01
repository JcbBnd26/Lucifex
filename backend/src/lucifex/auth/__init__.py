"""Authentication and security primitives.

This package holds stateless cryptographic helpers — password hashing,
session token generation, constant-time comparison. It does NOT touch
the database, perform IO, or own any global state beyond a single
`argon2.PasswordHasher` instance.

Higher-level concerns live elsewhere:

- Persistence (User, Session models, queries) → `lucifex.db`
- Business logic (register, authenticate, create_session, revoke) →
  `lucifex.core.auth` (future chunk)
- HTTP routes and middleware → `lucifex.api` (future chunk)
"""

from lucifex.auth.passwords import hash_password, needs_rehash, verify_password
from lucifex.auth.tokens import (
    SESSION_TOKEN_BYTES,
    constant_time_compare,
    generate_session_token,
    hash_session_token,
)

__all__ = [
    "SESSION_TOKEN_BYTES",
    "constant_time_compare",
    "generate_session_token",
    "hash_password",
    "hash_session_token",
    "needs_rehash",
    "verify_password",
]
