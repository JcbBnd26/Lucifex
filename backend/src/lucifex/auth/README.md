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
