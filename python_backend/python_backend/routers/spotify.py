from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse, Response
from typing import Optional, Literal
from pydantic import BaseModel


from aiohttp import ClientSession
from contextlib import asynccontextmanager

from python_backend.lib.spotify_helper import SpotifyHelper, SpotifyError, Track, TopArtist


spotify_helper: Optional[SpotifyHelper] = None
client_session: Optional[ClientSession] = None

@asynccontextmanager
async def lifespan(app: APIRouter):
    print("startup")
    global client_session, spotify_helper
    client_session = ClientSession()
    spotify_helper = SpotifyHelper(client_session)

    yield

    await client_session.close()
    spotify_helper = None

    print("close")

router = APIRouter(prefix="/spotify", lifespan=lifespan)

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
                "example": {"error": "SpotifyError", "message": "Authorization with access token unsuccessful"}
            }
        }
    }
}

@router.get(
            "/currently-playing",
            responses={
                204: {"description": "Nothing is currently playing on user's spotify"}, 
                **spotify_error_response
            }
        )
async def currently_playing() -> Optional[Track]:
    """Get the currently playing track from user's spotify"""

    if spotify_helper:
        try:
            track = await spotify_helper.get_currently_playing()

            if track == None:
                return Response(status_code=204) # 204 No Content
            
            return track
        except SpotifyError as e:
            return JSONResponse({
                    "error": "SpotifyError",
                    "message": e.args[0]["message"]
                },
                status_code=502
            )

@router.get("/last-played", responses=spotify_error_response)
async def last_played() -> Optional[Track]:
    """Get the last played track from user's spotify"""
    
    if spotify_helper:
        try:
            track = await spotify_helper.get_last_played_track()

            return track
        except SpotifyError as e:
            return JSONResponse({
                    "error": "SpotifyError",
                    "message": e.args[0]["message"]
                },
                status_code=502
            )
    
@router.get("/top-{type}", responses=spotify_error_response)
async def top_type(
            type: Literal["artists", "tracks"],
            limit: int = Query(default=10, ge=1, le=50)
        ) -> Optional[list[Track] | list[TopArtist]]:
    """Get the top `type` from user's spotify"""

    # check if type is correct
    if type not in ["artists", "tracks"]:
        return JSONResponse(
            {
                "error": "wrong path parameter",
                "message": "path paramter `type` must one of `artists` or `tracks`"
            },
            status_code=400 # 400 Bad Request
        )
    
    if spotify_helper:
        try:
            if type == "artists":
                top_user_artists = await spotify_helper.get_top_month_artists(limit=limit)

                return top_user_artists
            elif type == "tracks":
                top_user_tracks = await spotify_helper.get_top_month_tracks(limit=limit)

                return top_user_tracks
        except SpotifyError as e:
            return JSONResponse({
                    "error": "SpotifyError",
                    "message": e.args[0]["message"]
                },
                status_code=502
            )