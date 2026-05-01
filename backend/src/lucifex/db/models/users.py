"""User and session models for authentication.

These tables exist from Phase 0. The system has only one operator (you), but
the schema is built as if it could be sold — auth and security are commercial
grade from day one.

See `docs/architecture.md` Tables 11 and 12, and `docs/decision_log.md` DEC-002
(commercial-grade from day one).
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import INET, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from lucifex.db.base import (
    Base,
    IdMixin,
    SoftDeleteMixin,
    TimestampMixin,
)

if TYPE_CHECKING:
    pass


# ---------------------------------------------------------------------------
# users
# ---------------------------------------------------------------------------


class User(Base, IdMixin, TimestampMixin, SoftDeleteMixin):
    """A human account that can log in.

    Single-user reality, multi-user schema. Roles are extensible strings,
    validated in application code. See DEC-011.
    """

    __tablename__ = "users"

    # Identity
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    email_verified_at: Mapped[datetime | None] = mapped_column(nullable=True)

    display_name: Mapped[str | None] = mapped_column(String(120), nullable=True)

    # Auth
    # NULL when the user only authenticates via OAuth (future).
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Authorization
    # Stored as string for extensibility; validated in application code.
    # Initial values: "owner", "admin", "operator", "viewer".
    role: Mapped[str] = mapped_column(String(32), nullable=False, default="operator")

    # MFA
    mfa_enabled: Mapped[bool] = mapped_column(default=False, nullable=False)
    mfa_secret_encrypted: Mapped[str | None] = mapped_column(String(512), nullable=True)

    # Login telemetry
    last_login_at: Mapped[datetime | None] = mapped_column(nullable=True)
    last_login_ip: Mapped[str | None] = mapped_column(INET, nullable=True)

    # Lockout state
    failed_login_count: Mapped[int] = mapped_column(default=0, nullable=False)
    locked_until: Mapped[datetime | None] = mapped_column(nullable=True)

    # Relationships
    sessions: Mapped[list[Session]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r} role={self.role!r}>"


# ---------------------------------------------------------------------------
# sessions
# ---------------------------------------------------------------------------


class Session(Base, IdMixin, TimestampMixin):
    """An active login session.

    One row per device or browser logged in. The actual session token is
    sent to the user's cookie; only the hash is stored here. If the database
    leaks, hashes can't be used to impersonate users.

    Sessions are not soft-deleted — they are revoked (revoked_at set) or
    they expire (expires_at passes). Both states keep the row for audit.
    """

    __tablename__ = "sessions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Token storage — hash only, never plaintext.
    session_token_hash: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True
    )

    # Lifecycle
    expires_at: Mapped[datetime] = mapped_column(nullable=False)
    last_active_at: Mapped[datetime | None] = mapped_column(nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(nullable=True)

    # Telemetry
    ip_address: Mapped[str | None] = mapped_column(INET, nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(512), nullable=True)

    # Relationships
    user: Mapped[User] = relationship(back_populates="sessions")

    def __repr__(self) -> str:
        return f"<Session id={self.id} user_id={self.user_id} expires_at={self.expires_at}>"
