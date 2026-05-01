"""Password hashing primitives.

Argon2id is the default password hashing algorithm for Lucifex. It is the
current OWASP-recommended choice for new applications, replacing bcrypt as
the default. Bcrypt remains in the dependency list for any future scenario
where we import accounts with bcrypt hashes — those would be re-hashed on
next successful login (see `needs_rehash`).

The `argon2.PasswordHasher()` instance below uses library-default cost
parameters (time, memory, parallelism). These defaults are tuned by the
argon2-cffi maintainers to the current OWASP guidance. We deliberately do
NOT override them here; if we ever want to tune costs to a specific
deployment target, that's a benchmarking task with its own decision record,
not a one-line change.

Functions in this module never log, persist, or echo the plaintext
password. Callers must not pass plaintexts through structured logging
contexts either.
"""

from __future__ import annotations

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError

# ---------------------------------------------------------------------------
# Hasher singleton
# ---------------------------------------------------------------------------
# A single PasswordHasher is reused across the process. PasswordHasher is
# stateless aside from its configured cost parameters, so reuse is safe and
# avoids reconstructing the same object on every request.

_hasher = PasswordHasher()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def hash_password(plaintext: str) -> str:
    """Hash a plaintext password with argon2id.

    Returns a self-describing hash string (starts with `$argon2id$...`)
    that encodes the algorithm, parameters, salt, and digest. The full
    string is what gets stored in `users.password_hash` — there is no
    separate salt column.

    The salt is randomly generated per call, so two hashes of the same
    plaintext will not be equal.
    """
    return _hasher.hash(plaintext)


def verify_password(plaintext: str, hash_: str) -> bool:
    """Verify a plaintext password against a stored hash.

    Returns True if the plaintext matches the hash, False otherwise.

    A malformed or unrecognized hash string is treated as a verification
    failure (returns False) rather than raising. This is a deliberate UX
    choice: from the user's perspective, "your password didn't work" is
    the right answer whether the stored hash is wrong-for-this-password
    or corrupt-and-unverifiable. Surfacing the difference would create
    HTTP 500s on otherwise normal login attempts and leak internal state.
    """
    try:
        return _hasher.verify(hash_, plaintext)
    except (VerifyMismatchError, InvalidHashError):
        return False


def needs_rehash(hash_: str) -> bool:
    """Return True if the hash was produced with outdated parameters.

    Call after a successful `verify_password` to opportunistically upgrade
    a stored hash when the library default cost parameters have been
    raised since the hash was originally created. The auth flow is
    expected to re-hash and persist when this returns True.
    """
    return _hasher.check_needs_rehash(hash_)


__all__ = [
    "hash_password",
    "needs_rehash",
    "verify_password",
]
