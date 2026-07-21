import uuid
from datetime import datetime, timezone

from pydantic import EmailStr
from sqlmodel import TIMESTAMP, Column, Field, SQLModel, text


class Admin(SQLModel, table=True):
	__tablename__ = "admins"  # pyright: ignore[reportAssignmentType]

	id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True, nullable=False)

	user: str = Field(nullable=False, min_length=3, max_length=64)
	email: EmailStr = Field(unique=True, index=True, nullable=False)
	hashed_password: str = Field(nullable=False)

	# We enforce UTC timezone at the application level
	created_at: datetime = Field(
		default_factory=lambda: datetime.now(timezone.utc),
		sa_column=Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP")),
	)
	updated_at: datetime = Field(
		default_factory=lambda: datetime.now(timezone.utc),
		sa_column=Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP")),
	)


class AdminSession(SQLModel, table=True):
	__tablename__ = "admin_sessions"  # pyright: ignore[reportAssignmentType]

	id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
	admin_id: uuid.UUID = Field(foreign_key="admins.id", index=True, ondelete="CASCADE")

	# Store the unique JWT ID token identifier
	jti: str = Field(index=True, unique=True)

	# Track metadata for security auditing
	user_agent: str | None = None
	ip_address: str | None = None

	created_at: datetime = Field(
		default_factory=lambda: datetime.now(timezone.utc),
		sa_column=Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP")),
	)
	expires_at: datetime = Field(
		sa_column=Column(TIMESTAMP(timezone=True), nullable=False),
	)


class BlacklistedIp(SQLModel, table=True):
	"""IPs temporarily cut off entirely after blowing through a rate limit repeatedly."""

	__tablename__ = "blacklisted_ips"  # pyright: ignore[reportAssignmentType]

	id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
	ip_address: str = Field(nullable=False, unique=True, index=True)
	reason: str = Field(nullable=False)

	created_at: datetime = Field(
		default_factory=lambda: datetime.now(timezone.utc),
		sa_column=Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP")),
	)
	expires_at: datetime = Field(
		sa_column=Column(TIMESTAMP(timezone=True), nullable=False, index=True),
	)
