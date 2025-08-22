from aiohttp import ClientSession
from pydantic import BaseModel, HttpUrl

from ..config import Config

CONFIG = Config()

_STATUS_SUCCESS = 200


class HardcoverBook(BaseModel):
	title: str
	author: str
	pages: int
	image: str
	link: HttpUrl


class HardcoverError(Exception):
	"""Error's related to Hardcover API."""

	def __init__(self, *args):
		super().__init__(*args)


class HardcoverApi:
	"""A client for interacting with the Hardcover GraphQL API.

	This class provides methods to query the Hardcover API for book-related
	data tied to a specific user. Authentication is handled via an API token
	provided in the configuration.
	"""

	GRAPHQL_URL = "https://api.hardcover.app/v1/graphql"

	def __init__(self) -> None:
		self._API_TOKEN: str = CONFIG["hardcover"]["api_token"]
		self._USER_ID: int = CONFIG["hardcover"]["user_id"]

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
			HardcoverBook: The currently reading book.

		Raises:
			HardcoverError: If the API request fails or returns a non-success status code.

		"""
		headers = {
			"Authorization": f"Bearer {self._API_TOKEN}",
		}

		# GraphQL is the stupidest thing ever. Just design better REST APIs with batch data request/post support.
		# GraphQL must be erased and forgotten!
		query = """
			{ list_books( where: { user_books: { user_id: { _eq: __USER_ID__ }, status_id: { _eq: 2 } } } distinct_on: book_id limit: 1 offset: 0 ) { book { title pages image { url } contributions { author { name } } slug } } }
		""".replace("__USER_ID__", str(self._USER_ID))  # noqa: E501

		response = await session.post(self.GRAPHQL_URL, headers=headers, json={"query": query})

		if response.status != _STATUS_SUCCESS:
			raise HardcoverError({"status_code": response.status, "message": await response.text()})

		data = await response.json()

		# Extract the list of books
		books = data.get("data", {}).get("list_books", [])

		# No currently reading book
		if not books:
			return None

		book_data = books[0]["book"]

		contributions = book_data.get("contributions", [])
		author = contributions[0]["author"].get("name") if contributions and contributions[0].get("author") else None

		return HardcoverBook(
			title=book_data.get("title"),
			author=author or "Unknown Author",
			pages=book_data.get("pages"),
			image=book_data.get("image", {}).get("url"),
			link=f"https://hardcover.app/books/{book_data.get('slug')}",
		)
