# Auth

Stateless cryptographic primitives. No database access, no IO, no business logic — just pure helpers that wrap well-tested libraries.

## What lives here

| Module | Purpose |
|--------|---------|
| `passwords.py` | Hash and verify passwords with argon2id. |
| `tokens.py` | Generate session tokens and hash them for storage. |

### Public API

```python
from lucifex.auth import (
    hash_password, verify_password, needs_rehash,
    generate_session_token, hash_session_token, constant_time_compare,
    SESSION_TOKEN_BYTES,
)
```

## Algorithm choices

- **Passwords → argon2id** (via `argon2-cffi`). Current OWASP recommendation. Library-default cost parameters; if those need tuning to a specific deployment we benchmark and record the decision rather than guessing.
- **Session tokens → `secrets.token_urlsafe(32)`** (256 bits) + **SHA-256** for the storage hash. The token already has full entropy; argon2 here would slow every authenticated request without adding security. The hash column is unique-indexed for O(log n) lookups.
- **Direct comparison → `hmac.compare_digest`** (exposed as `constant_time_compare`). Reserved for any path that must compare two secret-derived strings directly instead of via an index lookup.

## Discipline

- We do not roll our own crypto. Every primitive in this folder is a thin call into `argon2-cffi`, `hashlib`, `secrets`, or `hmac`.
- Plaintext passwords and session tokens are never logged, never put in structured-log contexts, never returned from any function except their immediate caller.
- `verify_password` deliberately swallows `InvalidHashError` and returns `False`. A corrupt or unrecognized stored hash should look like "wrong password" to the caller, not an HTTP 500.

## Where the rest of auth lives

- **Persistence** (User and Session tables, password and session-hash columns, queries): `src/lucifex/db/`.
- **Business logic** (register, authenticate, create_session, revoke_session, lockout, MFA): `src/lucifex/core/auth/` — future chunk.
- **HTTP transport** (login, logout, session middleware, dependency injection of the current user): `src/lucifex/api/` — future chunk.

## Encryption strategy (for OAuth tokens and other at-rest secrets)

Symmetric encryption with a key sourced from `LUCIFEX_ENCRYPTION_KEY` (see `.env.example`) and the `cryptography` library's Fernet primitive. Implementation arrives with the first feature that actually needs to encrypt a credential — likely a platform OAuth chunk.
# Auth

Authentication and security primitives.

## What lives here

- Password hashing (bcrypt or argon2)
- JWT or session token handling
- OAuth flow helpers (delegated to platform/provider adapters where appropriate)
- Encryption/decryption for secrets stored in the database
- Role and permission checking
- Rate limiting helpers

## Discipline

This folder is small but critical. Mistakes here are security holes.

Every function in this folder is a thin wrapper around well-tested libraries (`bcrypt`, `cryptography`, `python-jose`). We do NOT roll our own crypto. Reading library documentation carefully is the skill here, not cleverness.

## Encryption strategy

The encryption key lives in environment variables (or a secrets manager in production). Tokens and API keys are encrypted before insert and decrypted on read. Database leak does NOT mean credential leak.
