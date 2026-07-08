import uuid
from datetime import datetime, timezone

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class Admin(SQLModel, table=True):
	__tablename__: str = "admins"  # pyright: ignore[reportIncompatibleVariableOverride]

	id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True, nullable=False)

	email: EmailStr = Field(unique=True, index=True, nullable=False)
	hashed_password: str = Field(nullable=False)

	# We enforce UTC timezone at the application level
	created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
	updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
