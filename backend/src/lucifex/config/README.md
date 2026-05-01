# Config

Settings, environment variables, and feature flags.

## What lives here

- `settings.py` — typed settings class (using `pydantic-settings`) that loads from environment variables
- `feature_flags.py` — runtime toggles for experimental features (added when needed)

## Typed settings

Don't read `os.environ.get("DATABASE_URL")` from random places in the codebase. Define a `Settings` class with typed fields. Validation happens at startup, not when something tries to use a missing setting at 3am. Every setting the app expects is documented in one place.

## Local development

Local development uses `.env` files (gitignored). Production uses real environment variables injected by the deployment platform. The `Settings` class works the same in both cases.

## Current settings

All variables use the `LUCIFEX_` prefix. See `.env.example` at the repo root for the canonical list and example values.

| Field | Env var | Type | Default | Notes |
|---|---|---|---|---|
| `database_url` | `LUCIFEX_DATABASE_URL` | `PostgresDsn` | required | Must use the `postgresql+asyncpg` driver. |
| `encryption_key` | `LUCIFEX_ENCRYPTION_KEY` | `SecretStr` | required | Minimum 32 characters. Generate with `secrets.token_urlsafe(32)`. |
| `env` | `LUCIFEX_ENV` | `Literal["development", "staging", "production"]` | `development` | |
| `log_level` | `LUCIFEX_LOG_LEVEL` | `Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]` | `INFO` | Stored only — wired into `structlog` in a later chunk. |

Use `get_settings()` (cached) to retrieve the singleton:

```python
from lucifex.config import get_settings

settings = get_settings()
print(settings.env)
```

Settings instances are frozen — assignment after load raises.
