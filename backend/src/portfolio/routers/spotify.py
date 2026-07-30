from typing import Literal

from fastapi import APIRouter, Depends, Query, Response, status

from ..deps import SpotifyDep
from ..integrations.spotify.schemas import TopArtist, Track
from ..schemas.errors import upstream_error_response
from ..security import rate_limit, require_viewer

router = APIRouter(prefix="/spotify", tags=["Spotify"], dependencies=[Depends(require_viewer), Depends(rate_limit())])

spotify_error_response = upstream_error_response(
	"The Spotify API returned an error", "Authorization with access token unsuccessful"
)


@router.get(
	"/currently-playing",
	response_model=Track,
	responses={204: {"description": "Nothing is currently playing on user's spotify"}, **spotify_error_response},
)
async def currently_playing(api: SpotifyDep) -> Track | Response:
	"""Get the currently playing track from user's spotify"""
	track = await api.get_currently_playing()
	if track is None:
		return Response(status_code=status.HTTP_204_NO_CONTENT)
	return track


@router.get(
	"/last-played",
	response_model=Track,
	responses={204: {"description": "No recent spotify track available"}, **spotify_error_response},
)
async def last_played(api: SpotifyDep) -> Track | Response:
	"""Get the last played track from user's spotify"""
	track = await api.get_last_played_track()
	if track is None:
		return Response(status_code=status.HTTP_204_NO_CONTENT)
	return track


@router.get(
	"/top/{type}",
	response_model=list[Track] | list[TopArtist],
	responses={204: {"description": "No top spotify data available"}, **spotify_error_response},
)
async def top_type(
	api: SpotifyDep,
	type: Literal["artists", "tracks"],
	limit: int = Query(default=10, ge=1, le=50),
) -> list[Track] | list[TopArtist] | Response:
	"""Get the top `type` from user's spotify"""
	if type == "artists":
		top = await api.get_top_month_artists(limit=limit)
	else:
		top = await api.get_top_month_tracks(limit=limit)

	if top is None:
		return Response(status_code=status.HTTP_204_NO_CONTENT)
	return top
