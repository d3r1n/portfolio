import uuid
from datetime import datetime, timezone

from pydantic import field_validator
from sqlmodel import TIMESTAMP, Column, Field, SQLModel, text


class CurrentLocation(SQLModel, table=True):
	"""Where the site owner currently is, set manually (e.g. via the admin dashboard)
	and used to look up conditions through `OpenWeatherApi`."""

	__tablename__ = "current_location"  # pyright: ignore[reportAssignmentType]

	id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

	# Coordinates are the functionally required part (they're what gets sent to the
	# weather API); a location with no coordinates isn't useful, so no row beats a null one.
	latitude: float = Field(ge=-90, le=90)
	longitude: float = Field(ge=-180, le=180)
	location_name: str = Field(nullable=False, min_length=3, max_length=128)

	created_at: datetime = Field(
		default_factory=lambda: datetime.now(timezone.utc),
		sa_column=Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP")),
	)
	updated_at: datetime = Field(
		default_factory=lambda: datetime.now(timezone.utc),
		sa_column=Column(
			TIMESTAMP(timezone=True),
			nullable=False,
			server_default=text("CURRENT_TIMESTAMP"),
			onupdate=lambda: datetime.now(timezone.utc),
		),
	)

	@field_validator("location_name", mode="before")
	def _validate_location_name(cls, v) -> str:
		"""Acceptable location names are non-empty comma seperated strings of letters, City/Country format
		e.g. "Istanbul, Turkey" or "New York, USA" or "London, UK"
		"""

		if not v or not isinstance(v, str):
			raise ValueError("Location name must be a non-empty string.")

		parts = [part.strip() for part in v.split(",")]
		if len(parts) != 2 or not all(parts):
			raise ValueError("Location name must be in 'City, Country' format.")

		return v
