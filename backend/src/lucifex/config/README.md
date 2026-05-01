# Config

Settings, environment variables, and feature flags.

## What lives here

- `settings.py` — typed settings class (using `pydantic-settings`) that loads from environment variables
- `feature_flags.py` — runtime toggles for experimental features (added when needed)

## Typed settings

Don't read `os.environ.get("DATABASE_URL")` from random places in the codebase. Define a `Settings` class with typed fields. Validation happens at startup, not when something tries to use a missing setting at 3am. Every setting the app expects is documented in one place.

## Local development

Local development uses `.env` files (gitignored). Production uses real environment variables injected by the deployment platform. The `Settings` class works the same in both cases.
