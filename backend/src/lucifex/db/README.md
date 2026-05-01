# Database Layer

SQLAlchemy models, Alembic migrations, and database session management.

## Structure

- `models/` — SQLAlchemy table definitions, one file per major table or domain
- `migrations/` — Alembic-generated change files, versioned in git
- `repositories/` — query helpers grouped by table (optional — added when query duplication appears)
- `session.py` — database connection setup and session factory
- `seed.py` — initial or test data seeding (added when needed)

## Migrations discipline

Every schema change is a migration. Migrations are versioned in git, applied in order, and reversible. Manual database edits are forbidden — they break reproducibility across environments.

## See also

- `docs/architecture.md` — full data model documentation (20 tables)
- `docs/decision_log.md` — DEC-008 (Postgres + SQLAlchemy + Alembic)
