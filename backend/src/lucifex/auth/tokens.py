"""Session token primitives.

A session token is an opaque random string that lives in the user's
cookie. The database stores only its SHA-256 hash, never the plaintext
token. If the database leaks, the hashes cannot be replayed as cookies.

Two distinct hashing roles exist in Lucifex auth:

- Passwords use argon2id (slow KDF, salted) because the input is
  low-entropy and adversaries get unlimited offline guesses against a
  leaked hash.
- Session tokens use SHA-256 (fast, unsalted) because the input is
  already 256 bits of cryptographically random entropy. Argon2 here
  would slow every authenticated request without adding security.

Token comparison on the lookup path uses a unique index on the hash
column — there is no per-user secret to leak through timing. The
`constant_time_compare` helper is exported for any future code path that
must compare two equal-length token-derived strings directly.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
from typing import Final

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

#: Number of random bytes per session token. 32 bytes = 256 bits of entropy.
#: `secrets.token_urlsafe(32)` produces a 43-character URL-safe string.
SESSION_TOKEN_BYTES: Final = 32


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def generate_session_token() -> str:
    """Return a fresh URL-safe session token.

    The token is 256 bits of OS-grade randomness encoded with the
    URL-safe base64 alphabet (no padding). It is suitable for use in a
    cookie value or an `Authorization: Bearer ...` header.

    Always pair with `hash_session_token` before storing.
    """
    return secrets.token_urlsafe(SESSION_TOKEN_BYTES)


def hash_session_token(token: str) -> str:
    """Return the SHA-256 hex digest of a session token.

    The result is a 64-character lowercase hex string. This is what
    gets persisted in `sessions.session_token_hash` and what the lookup
    path queries by — never the plaintext token.

    Deterministic: the same input always produces the same output.
    """
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def constant_time_compare(a: str, b: str) -> bool:
    """Compare two strings in constant time relative to their length.

    Wraps `hmac.compare_digest`. Use whenever code must compare two
    secret-derived strings directly (rather than via a database index
    lookup) to avoid leaking information through timing.
    """
    return hmac.compare_digest(a, b)


__all__ = [
    "SESSION_TOKEN_BYTES",
    "constant_time_compare",
    "generate_session_token",
    "hash_session_token",
]
