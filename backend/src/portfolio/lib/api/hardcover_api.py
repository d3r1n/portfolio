from aiohttp import ClientSession
from loguru import logger
from pydantic import BaseModel, HttpUrl, ValidationError

from ..util.config import Config

_STATUS_SUCCESS = 200


class HardcoverBook(BaseModel):
	title: str
	author: str
	pages: int | None = None
	image_url: HttpUrl | None = None
	image_dominant_color: str | None = None
	progress: float | None = None
	link: HttpUrl


class HardcoverError(Exception):
	"""Errors related to Hardcover API."""

	def __init__(self, *args):
		super().__init__(*args)


class HardcoverApi:
	"""A client for interacting with the Hardcover GraphQL API.

	This class provides methods to query the Hardcover API for book-related
	data tied to a specific user. Authentication is handled via an API token
	provided in the configuration.
	"""

	GRAPHQL_URL: str = "https://api.hardcover.app/v1/graphql"

	def __init__(self, config: Config) -> None:
		self._USER_ID: str = config.hardcover.user_id
		self._API_TOKEN: str = config.hardcover.api_token

	@staticmethod
	def _extract_error_message(payload: dict[str, object]) -> str | None:
		errors = payload.get("errors")
		if not isinstance(errors, list) or not errors:
			return None

		first_error = errors[0]
		if not isinstance(first_error, dict):
			return None

		message = first_error.get("message")
		return message if isinstance(message, str) else None

	async def get_currently_reading_book(
		self,
		session: ClientSession,
	) -> HardcoverBook | None:
		"""Fetch the book the user is currently reading from Hardcover.

		The method queries the Hardcover GraphQL API for the user's book list,
		filtering by the "currently reading" status. If a book is found, it is
		returned as a `HardcoverBook` instance.

		Args:
		    session (ClientSession): An aiohttp client session used to send the request.

		Returns:
		    HardcoverBook | None: The currently reading book, or None if none found.

		Raises:
		    HardcoverError: If the API request fails or returns a non-success status code.
		"""
		if not self._API_TOKEN:
			logger.warning("Hardcover API token is not configured. Skipping request.")
			return None

		headers = {
			"content-type": "application/json",
			"Authorization": f"Bearer {self._API_TOKEN}",
		}

		query = """
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

		response = await session.post(self.GRAPHQL_URL, headers=headers, json={"query": query})

		if response.status != _STATUS_SUCCESS:
			raise HardcoverError({"status_code": response.status, "message": await response.text()})

		data = await response.json()
		logger.debug(f"Hardcover API response data: {data}")
		error_message = self._extract_error_message(data)
		if error_message:
			raise HardcoverError({"status_code": _STATUS_SUCCESS, "message": error_message})

		logger.info("Hardcover API book request hit")

		me_data = data.get("data", {}).get("me", {})
		if me_data is None or (isinstance(me_data, list) and not me_data):
			logger.warning("Hardcover API returned empty user data (me is null or empty).")
			return None

		# Clean up handling if 'me' arrives as a list or a single dictionary context
		me_dict = me_data[0] if isinstance(me_data, list) else me_data
		books = me_dict.get("user_books", []) if isinstance(me_dict, dict) else []

		if not books:
			return None

		first_book = books[0] if isinstance(books[0], dict) else {}
		book_data = first_book.get("book", {}) if isinstance(first_book, dict) else {}
		if not isinstance(book_data, dict):
			return None

		contributions = book_data.get("contributions", [])
		authors = []
		for contribution in contributions:
			if isinstance(contribution, dict) and contribution.get("author"):
				author_data = contribution["author"]
				if isinstance(author_data, dict) and author_data.get("name"):
					authors.append(author_data["name"])

		author = ", ".join(authors) if authors else "Unknown Author"
		image_data = book_data.get("image", {}) if isinstance(book_data.get("image"), dict) else {}
		reads = first_book.get("user_book_reads", []) if isinstance(first_book, dict) else []

		progress = None
		for read in reads:
			if isinstance(read, dict):
				p = read.get("progress")
				if isinstance(p, (int, float)):
					progress = p
					break

		if isinstance(progress, (int, float)) and progress <= 1:
			progress = progress * 100

		title = book_data.get("title")
		slug = book_data.get("slug")
		if not isinstance(title, str) or not isinstance(slug, str):
			return None

		try:
			return HardcoverBook(
				title=title,
				author=author,
				pages=book_data.get("pages") if isinstance(book_data.get("pages"), int) else None,
				image_url=image_data.get("url") if image_data.get("url") else None,
				link=f"https://hardcover.app/books/{slug}",  # pyright: ignore[reportArgumentType]
				progress=progress if isinstance(progress, (int, float)) else None,
				image_dominant_color=image_data.get("color") if isinstance(image_data.get("color"), str) else None,
			)
		except ValidationError as exc:
			logger.error(f"Pydantic Validation failed parsing HardcoverBook. Errors: {exc.errors()}")
			raise HardcoverError(
				{
					"status_code": _STATUS_SUCCESS,
					"message": f"Hardcover response validation failed: {exc.errors()}",
				}
			) from exc
