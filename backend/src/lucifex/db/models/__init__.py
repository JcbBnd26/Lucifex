"""Lucifex SQLAlchemy models.

Importing models here ensures Alembic's autogenerate sees them when
comparing the declarative metadata to the database state.

Add new model imports to the registration block as the schema grows.
"""

from lucifex.db.models.users import Session, User

__all__ = [
    "Session",
    "User",
]
