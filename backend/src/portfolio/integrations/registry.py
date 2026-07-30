from dataclasses import dataclass

from aiohttp import ClientSession

from ..core.config import Config
from .hardcover.client import HardcoverApi
from .openweather.client import OpenWeatherApi
from .spotify.client import SpotifyApi


@dataclass
class Integrations:
	"""All third-party API clients plus the shared aiohttp session they use.

	Constructed once in the app lifespan and stored on `app.state` — the single
	untyped hop; everything past it is type-checked. Adding an integration is one
	field here, one line in `create()`, and a dependency alias in `deps.py`.
	"""

	session: ClientSession
	spotify: SpotifyApi
	hardcover: HardcoverApi
	openweather: OpenWeatherApi

	@classmethod
	def create(cls, config: Config) -> "Integrations":
		# Must be called from a running event loop (aiohttp binds the session to it).
		# One shared session = one connection pool + DNS cache for every client;
		# a client that ever needs its own session (timeouts, proxy) gets it here.
		session = ClientSession()
		return cls(
			session=session,
			spotify=SpotifyApi(config, session),
			hardcover=HardcoverApi(config, session),
			openweather=OpenWeatherApi(config, session),
		)

	async def close(self) -> None:
		await self.session.close()
