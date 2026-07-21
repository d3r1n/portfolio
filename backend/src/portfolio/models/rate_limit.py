import uuid
from datetime import datetime, timezone

from sqlmodel import TIMESTAMP, Column, Field, SQLModel, text


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
