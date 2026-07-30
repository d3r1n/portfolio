from typing import Any

from aiohttp import ClientSession
from loguru import logger
from pydantic import BaseModel, Field, ValidationError

from ...core.config import Config
from .. import UpstreamError
from .schemas import HardcoverBook


class HardcoverError(UpstreamError):
	service = "Hardcover"


_CURRENTLY_READING_QUERY = """
	query books {
	  me {
		user_books(limit: 1, where: {status_id: {_eq: 2}}, order_by: {updated_at: desc}) {
		  book {
			title
			image {
			  url
			  color
			}
			slug
			contributions {
			  author {
				name
			  }
			}
			pages
		  }
		  user_book_reads {
			progress
		  }
		}
	  }
	}
"""


# Private models mirroring the GraphQL response shape — they exist purely so
# pydantic does the defensive parsing instead of hand-written isinstance checks.
class _Image(BaseModel):
	url: str | None = None
	color: str | None = None


class _Author(BaseModel):
	name: str | None = None


class _Contribution(BaseModel):
	author: _Author | None = None


class _Book(BaseModel):
	title: str
	slug: str
	image: _Image | None = None
	contributions: list[_Contribution] = Field(default_factory=list)
	pages: int | None = None


class _Read(BaseModel):
	progress: float | None = None


class _UserBook(BaseModel):
	book: _Book
	user_book_reads: list[_Read] = Field(default_factory=list)


def _to_book(user_book: _UserBook) -> HardcoverBook:
	book = user_book.book

	authors = [c.author.name for c in book.contributions if c.author and c.author.name]

	progress = next((read.progress for read in user_book.user_book_reads if read.progress is not None), None)
	if progress is not None and progress <= 1:
		progress *= 100  # Hardcover sometimes reports a 0-1 fraction instead of a percentage

	image = book.image or _Image()

	return HardcoverBook(
		title=book.title,
		author=", ".join(authors) if authors else "Unknown Author",
		pages=book.pages,
		image_url=image.url or None,
		image_dominant_color=image.color,
		progress=progress,
		link=f"https://hardcover.app/books/{book.slug}",  # pyright: ignore[reportArgumentType]
	)


class HardcoverApi:
	"""Client for the Hardcover GraphQL API, bound to the app-wide aiohttp session.

	Queries book-related data for the configured user; authentication is a
	bearer token from the configuration.
	"""

	GRAPHQL_URL = "https://api.hardcover.app/v1/graphql"

	def __init__(self, config: Config, session: ClientSession) -> None:
		self._session = session
		self._api_token = config.hardcover.api_token

	async def get_currently_reading_book(self) -> HardcoverBook | None:
		"""The book the user is currently reading, or None if there isn't one."""
		if not self._api_token:
			logger.warning("Hardcover API token is not configured. Skipping request.")
			return None

		response = await self._session.post(
			self.GRAPHQL_URL,
			headers={"Authorization": f"Bearer {self._api_token}"},
			json={"query": _CURRENTLY_READING_QUERY},
		)

		if response.status != 200:
			raise HardcoverError(await response.text(), status_code=response.status)

		payload = await response.json()
		logger.debug(f"Hardcover API response data: {payload}")

		if message := _graphql_error(payload):
			raise HardcoverError(message)

		# `me` arrives as a list or a single object depending on the API mood — normalize.
		me = payload.get("data", {}).get("me") or {}
		if isinstance(me, list):
			me = me[0] if me else {}
		user_books = me.get("user_books") or []

		if not user_books:
			return None

		try:
			return _to_book(_UserBook.model_validate(user_books[0]))
		except ValidationError as exc:
			logger.error(f"Failed parsing Hardcover response: {exc}")
			raise HardcoverError(f"Hardcover response validation failed: {exc.errors()}") from exc


def _graphql_error(payload: dict[str, Any]) -> str | None:
	"""First error message in a GraphQL error payload, if any."""
	errors = payload.get("errors")
	if isinstance(errors, list) and errors and isinstance(errors[0], dict):
		message = errors[0].get("message")
		if isinstance(message, str):
			return message
	return None
