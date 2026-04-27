import tomllib
from typing import Literal

from pydantic import BaseModel, ConfigDict


class SpotifyConfig(BaseModel):
	client_id: str
	client_secret: str
	refresh_token: str


class HardcoverConfig(BaseModel):
	user_id: str
	api_token: str


class ApiConfig(BaseModel):
	allowed_origins: tuple[str]


class Config(BaseModel):
	spotify: SpotifyConfig
	hardcover: HardcoverConfig
	api: ApiConfig

	model_config = ConfigDict(frozen=True)


def load_config(deployment_mode: Literal["DEV", "PROD"] = "DEV") -> Config:
	if deployment_mode == "DEV":
		file_name = "config.dev.toml"
	elif deployment_mode == "PROD":
		file_name = "config.prod.toml"

	with open(file_name, "rb") as f:
		data = tomllib.load(f)

	return Config(**data)
