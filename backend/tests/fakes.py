"""Minimal aiohttp stand-ins for exercising the integration clients offline."""

from typing import Any


class FakeResponse:
	def __init__(self, status: int = 200, json_data: Any = None, text: str = ""):
		self.status = status
		self._json = json_data
		self._text = text

	async def json(self) -> Any:
		return self._json

	async def text(self) -> str:
		return self._text


class FakeSession:
	"""Returns queued responses for GET and a fixed response for POST."""

	def __init__(self, get_responses: list[FakeResponse] | None = None, post_response: FakeResponse | None = None):
		self._get_responses = list(get_responses or [])
		self._post_response = post_response
		self.requests: list[tuple[str, str, dict]] = []

	async def get(self, url: str, **kwargs) -> FakeResponse:
		self.requests.append(("GET", url, kwargs))
		return self._get_responses.pop(0)

	async def post(self, url: str, **kwargs) -> FakeResponse:
		self.requests.append(("POST", url, kwargs))
		assert self._post_response is not None, "unexpected POST"
		return self._post_response
