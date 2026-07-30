from typing import Any

from pydantic import BaseModel


class UpstreamErrorMessage(BaseModel):
	"""Envelope returned (502) whenever a third-party API call fails — see the
	`UpstreamError` handler in `main.py`."""

	error: str
	message: str


def upstream_error_response(description: str, example_message: str) -> dict[int | str, dict[str, Any]]:
	"""OpenAPI `responses` entry documenting the shared 502 envelope for a router."""
	return {
		502: {
			"model": UpstreamErrorMessage,
			"description": description,
			"content": {
				"application/json": {
					"example": {"error": "UpstreamError", "message": example_message},
				},
			},
		},
	}
