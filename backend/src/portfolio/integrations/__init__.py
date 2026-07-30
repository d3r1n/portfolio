from typing import ClassVar


class UpstreamError(Exception):
	"""Failure talking to a third-party API.

	Raised by the integration clients and mapped to a single 502 response by the
	app-level exception handler in `main.py` — routers never handle these themselves.
	"""

	service: ClassVar[str] = "upstream"

	def __init__(self, message: str, status_code: int | None = None) -> None:
		super().__init__(message)
		self.message = message
		self.status_code = status_code
