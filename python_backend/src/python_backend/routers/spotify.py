from typing import Annotated, Literal

from aiohttp import ClientSession
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from ..deps import _get_spotify_api, get_client_session, get_spotify_service
from ..lib.api.spotify_api import (
	SpotifyApi,
	SpotifyError,
	TopArtist,
	Track,
)

# Set to None to be declared when the lifecycle of the route starts

router = APIRouter(prefix="/spotify")


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


@router.get(
	"/currently-playing",
	responses={
		204: {"description": "Nothing is currently playing on user's spotify"},
		**spotify_error_response,
	},
)
async def currently_playing(
	service: Annotated[tuple[SpotifyApi, ClientSession], Depends(get_spotify_service)],
) -> Track | None:
	"""Get the currently playing track from user's spotify"""
	api, session = service

	if api and session:
		try:
			track = await api.get_currently_playing(session)

			if track is None:
				return Response(status_code=204)  # 204 No Content

			return track
		except SpotifyError as e:
			return JSONResponse(
				{"error": "SpotifyError", "message": e.args[0]["message"]},
				status_code=502,
			)


@router.get("/last-played", responses=spotify_error_response)
async def last_played(
	service: Annotated[tuple[SpotifyApi, ClientSession], Depends(get_spotify_service)],
) -> Track | None:
	"""Get the last played track from user's spotify"""
	api, session = service

	if api and session:
		try:
			track = await api.get_last_played_track(session)

			return track
		except SpotifyError as e:
			return JSONResponse(
				{"error": "SpotifyError", "message": e.args[0]["message"]},
				status_code=502,
			)


@router.get("/top-{type}", responses=spotify_error_response)
async def top_type(
	service: Annotated[tuple[SpotifyApi, ClientSession], Depends(get_spotify_service)],
	type: Literal["artists", "tracks"],
	limit: int = Query(default=10, ge=1, le=50),
) -> list[Track] | list[TopArtist] | None:
	"""Get the top `type` from user's spotify"""
	# check if type is correct
	if type not in ["artists", "tracks"]:
		return JSONResponse(
			{
				"error": "wrong path parameter",
				"message": "path paramter `type` must one of `artists` or `tracks`",
			},
			status_code=400,  # 400 Bad Request
		)

	api, session = service

	if api and session:
		try:
			if type == "artists":
				top_user_artists = await api.get_top_month_artists(session, limit=limit)

				return top_user_artists
			if type == "tracks":
				top_user_tracks = await api.get_top_month_tracks(session, limit=limit)

				return top_user_tracks
		except SpotifyError as e:
			return JSONResponse(
				{"error": "SpotifyError", "message": e.args[0]["message"]},
				status_code=502,
			)
