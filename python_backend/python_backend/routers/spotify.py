from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse, Response
from typing import Optional
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

@router.get("/currently-playing")
async def currently_playing() -> Optional[Track]:
    if spotify_helper:
        track = await spotify_helper.get_currently_playing()

        if track == None:
            return Response(status_code=204) # 204 No Content
        
        return track

@router.get("/last-played")
async def last_played() -> Optional[Track]:
    if spotify_helper:
        track = await spotify_helper.get_last_played_track()

        return track
    
@router.get("/top-{_type}")
async def top_type(_type: str, limit: int = Query(default=10, ge=1, le=50)) -> Optional[list[Track] | list[TopArtist]]:
    # check if type is correct
    if _type not in ["artists", "tracks"]:
        return JSONResponse(
            {
                "error": "wrong path parameter",
                "error_msg": "path paramter `_type` must one of `artists` or `user`"
            },
            status_code=400 # 400 Bad Request
        )

    if spotify_helper:

        if _type == "artists":
            top_user_artists = await spotify_helper.get_top_month_artists(limit=limit)

            return top_user_artists
        elif _type == "tracks":
            top_user_tracks = await spotify_helper.get_top_month_tracks(limit=limit)

            return top_user_tracks