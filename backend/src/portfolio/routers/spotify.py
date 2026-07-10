from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from ..deps import SpotifyService, get_spotify_service
from ..lib.integrations.spotify_api import (
	SpotifyError,
	TopArtist,
	Track,
)
from ..lib.security import require_viewer

# Set to None to be declared when the lifecycle of the route starts

router = APIRouter(prefix="/spotify", tags=["Spotify"], dependencies=[Depends(require_viewer)])


class SpotifyErrorMessage(BaseModel):
	error: str
	message: str


# spotify error response for OpenAPI
spotify_error_response = {
	502: {
		"model": SpotifyErrorMessage,
		"description": "The Spotify API returned an error",
		"content": {
			"application/json": {
				"example": {
					"error": "SpotifyError",
					"message": "Authorization with access token unsuccessful",
				},
			},
		},
	},
}


def _spotify_error_message(error: SpotifyError) -> str:
	if not error.args:
		return "Unknown spotify service error"
	detail = error.args[0]
	if isinstance(detail, dict):
		message = detail.get("message")
		if isinstance(message, str):
			return message
	return "Unknown spotify service error"


@router.get(
	"/currently-playing",
	response_model=Track,
	responses={
		204: {"description": "Nothing is currently playing on user's spotify"},
		**spotify_error_response,
	},
)
async def currently_playing(
	service: Annotated[SpotifyService, Depends(get_spotify_service)],
) -> Track | Response:
	"""Get the currently playing track from user's spotify"""
	api, session = service

	try:
		track = await api.get_currently_playing(session)
		if track is None:
			return Response(status_code=status.HTTP_204_NO_CONTENT)
		return track
	except SpotifyError as error:
		return JSONResponse(
			status_code=status.HTTP_502_BAD_GATEWAY,
			content={"error": "SpotifyError", "message": _spotify_error_message(error)},
		)


@router.get(
	"/last-played",
	response_model=Track,
	responses={204: {"description": "No recent spotify track available"}, **spotify_error_response},
)
async def last_played(
	service: Annotated[SpotifyService, Depends(get_spotify_service)],
) -> Track | Response:
	"""Get the last played track from user's spotify"""
	api, session = service

	try:
		track = await api.get_last_played_track(session)
		if track is None:
			return Response(status_code=status.HTTP_204_NO_CONTENT)
		return track
	except SpotifyError as error:
		return JSONResponse(
			status_code=status.HTTP_502_BAD_GATEWAY,
			content={"error": "SpotifyError", "message": _spotify_error_message(error)},
		)


@router.get(
	"/top/{type}",
	response_model=list[Track] | list[TopArtist],
	responses={
		204: {"description": "No top spotify data available"},
		**spotify_error_response,
	},
)
async def top_type(
	service: Annotated[SpotifyService, Depends(get_spotify_service)],
	type: Literal["artists", "tracks"],
	limit: int = Query(default=10, ge=1, le=50),
) -> list[Track] | list[TopArtist] | Response:
	"""Get the top `type` from user's spotify"""
	api, session = service

	try:
		if type == "artists":
			top_user_artists = await api.get_top_month_artists(session, limit=limit)
			if top_user_artists is None:
				return Response(status_code=status.HTTP_204_NO_CONTENT)
			return top_user_artists

		top_user_tracks = await api.get_top_month_tracks(session, limit=limit)
		if top_user_tracks is None:
			return Response(status_code=status.HTTP_204_NO_CONTENT)
		return top_user_tracks
	except SpotifyError as error:
		return JSONResponse(
			status_code=status.HTTP_502_BAD_GATEWAY,
			content={"error": "SpotifyError", "message": _spotify_error_message(error)},
		)
