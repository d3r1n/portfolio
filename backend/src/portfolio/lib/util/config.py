from secrets import token_hex
from typing import Literal

from loguru import logger
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

type DeploymentMode = Literal["DEV", "PROD", "TEST"]


class SpotifyConfig(BaseModel):
	client_id: str
	client_secret: str
	refresh_token: str


class HardcoverConfig(BaseModel):
	user_id: str
	api_token: str


class ApiConfig(BaseModel):
	# Pydantic-settings natively handles parsing comma-separated strings into tuples
	# if you type hint it as a tuple! No custom parsers needed.
	allowed_origins: tuple[str, ...] = Field(default=("*",))


class SecurityConfig(BaseModel):
	default_rate_limit_per_minute: int = Field(default=120, ge=10, le=5000)
	auth_rate_limit_per_minute: int = Field(default=20, ge=5, le=1000)
	auto_blacklist_multiplier: int = Field(default=3, ge=2, le=20)
	auto_blacklist_minutes: int = Field(default=30, ge=1, le=1440)

	jwt_secret_key: str = Field(default_factory=lambda: token_hex(32), frozen=True)
	jwt_algorithm: str = Field(default="HS256", frozen=True)
	jwt_viewer_token_expire_minutes: int = Field(default=30, ge=1, le=120, frozen=True)


class Config(BaseSettings):
	model_config = SettingsConfigDict(
		env_prefix="BACKEND_",
		env_nested_delimiter="__",
		frozen=True,
	)

	# Use validation_alias to explicitly match the exact names in your .env
	deployment_mode: DeploymentMode = Field(default="DEV", validation_alias="DEPLOYMENT_MODE")
	db_url: str = Field(validation_alias="DB_URL")

	# For nested objects, validation_alias maps the prefix of the environment variables
	spotify: SpotifyConfig
	hardcover: HardcoverConfig

	api: ApiConfig = Field(default_factory=ApiConfig)
	security: SecurityConfig = Field(default_factory=SecurityConfig)


def load_config() -> Config:
	"""Load the configuration from environment variables and return a Config object."""
	return Config()  # pyright: ignore[reportCallIssue]
