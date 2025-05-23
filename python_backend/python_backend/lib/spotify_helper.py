from aiohttp import ClientSession
from pydantic import BaseModel, Field, HttpUrl, validate_call, ConfigDict
from typing import Annotated

from datetime import datetime, timedelta
import base64

from .config_helper import Config

config = Config()


class SpotifyError(Exception):
    """
    Base class for exceptions raised by spotify_helper module
    """

    def __init__(self, *args):
        super().__init__(*args)


class Track(BaseModel):
    """
    Dataclass representing the a track returned from the spotify api.

    Most of the data from the original response isn't included here since
    we're only interested in data our application actually requires.
    """

    name: str
    artists: list[str]
    track_url: HttpUrl
    is_playing: bool | None = Field(default=None)
    album_name: str
    album_image: HttpUrl
    duration_ms: int | None = Field(default=None)
    progress_ms: int | None = Field(default=None)


class TopArtist(BaseModel):
    """
    Dataclass representing an artist returned from the spotify's top artists response
    """

    name: str
    url: HttpUrl
    image: HttpUrl


# to be used with map to get only the artist name
def format_artists(artist: dict) -> str:
    return artist["name"]


class SpotifyHelper:
    """
    A helper class to interact with the Spotify API.

    Functionality of this class is as follows, refreshing/creating access tokens, fetching the currently playing track,
    fetching the last played track (to be used if there's no currently playing track),
    fetching the top artists of the month, fetching the top tracks of the month.
    """

    BASE_URL: str = "https://api.spotify.com/v1"
    AUTH_URL: str = "https://accounts.spotify.com/api"

    def __init__(self, session: ClientSession):
        """
        Initializes the SpotifyHelper instance by loading client credentials and setting access token properties.

        # Parameters
            **session** (*ClientSession*): an aiohttp ClientSession to make the requests

        """
        self._CLIENT_ID: str = config["spotify"]["client_id"]
        self._CLIENT_SECRET: str = config["spotify"]["client_secret"]
        self._REFRESH_TOKEN: str = config["spotify"]["refresh_token"]

        self._access_token: str = None
        self._expiry_time: datetime = None
        self.session = session

    # @validate_call(config= ConfigDict(arbitrary_types_allowed=True))
    async def _refresh_access_token(self):
        """
        Refreshes the Spotify access token if it has expired.

        # Raises
            **SpotifyError**: if response status code is anything except `200 (OK)`
        """

        # check if current token is expired before requesting a new access token
        # so we don't waste a token thats still valid
        now = datetime.now()
        if self._expiry_time and now <= self._expiry_time:
            return

        url = self.AUTH_URL + "/token"

        basic_auth: str = base64.b64encode(
            f"{self._CLIENT_ID}:{self._CLIENT_SECRET}".encode()
        ).decode("utf-8")

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "Basic " + basic_auth,
        }

        payload = {
            "grant_type": "refresh_token",
            "refresh_token": self._REFRESH_TOKEN,
        }

        response = await self.session.post(url, headers=headers, data=payload)

        # Error handling
        if response.status != 200:
            raise SpotifyError(
                {"status_code": response.status, "message": await response.text()}
            )

        json_data = await response.json()
        self._access_token = json_data["access_token"]

        # set the expiry to current time + spotify's expires_in
        current_time = datetime.now()
        self._expiry_time = current_time + timedelta(seconds=json_data["expires_in"])

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    async def get_currently_playing(self) -> Track | None:
        """
        Retrieves the user's currently playing track.

        # Returns
            **Track**: The currently playing track details.

            **None**: when there's nothing playing

        # Raises
            **SpotifyError**: if response status code is anything except `200 (OK)`
        """

        await self._refresh_access_token()

        url = self.BASE_URL + "/me/player/currently-playing"

        headers = {"Authorization": f"Bearer {self._access_token}"}

        response = await self.session.get(url, headers=headers)

        # if status code is not 200 or 204 raise exception
        if response.status not in [200, 204]:
            raise SpotifyError(
                {"status_code": response.status, "message": await response.text()}
            )

        # 204 (No Content), request was successful but there's no content to be returned
        elif response.status == 204:
            return None

        json_data = await response.json()

        currently_playing = Track(
            name=json_data["item"]["name"],
            is_playing=json_data["is_playing"],
            progress_ms=json_data["progress_ms"],
            duration_ms=json_data["item"]["duration_ms"],
            album_name=json_data["item"]["album"]["name"],
            album_image=json_data["item"]["album"]["images"][0]["url"],
            artists=map(format_artists, json_data["item"]["artists"]),
            track_url=f"https://open.spotify.com/track/{json_data['item']['uri'].split(':')[2]}",
        )

        return currently_playing

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    async def get_last_played_track(self) -> Track | None:
        """
        Retrieves the user's last played track

        # Returns
            **Track**: last played track details. this Track object doesn't include duration, progress, and play/resume data

            **None**: if there's no last played track (if status code is `204 (No Content)`)

        # Raises
            **SpotifyError**: if response status code is anything except `200 (OK)`
        """

        await self._refresh_access_token()

        url = self.BASE_URL + "/me/player/recently-played"

        url_params = {"limit": 5}

        headers = {"Authorization": f"Bearer {self._access_token}"}

        response = await self.session.get(url, headers=headers, params=url_params)

        if response.status not in [204, 200]:
            raise SpotifyError(
                {"status_code": response.status, "message": await response.text()}
            )
        elif response.status == 204:  # 204 (No Content)
            return None

        json_data = await response.json()

        track0 = json_data["items"][0]["track"]

        last_played_track = Track(
            name=track0["name"],
            album_name=track0["album"]["name"],
            album_image=track0["album"]["images"][0]["url"],
            artists=map(format_artists, track0["artists"]),
            track_url=f"https://open.spotify.com/track/{track0['uri'].split(':')[2]}",
        )

        return last_played_track

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    async def get_top_month_tracks(
        self,
        *,  # pydantic keyword only
        limit: Annotated[int, Field(default=10, ge=1, le=50)],
    ) -> list[Track] | None:
        """
        Retrieves user's top tracks of the last 4 weeks

        # Parameters
            **limit** (*int*): the limit lenght of the tracks returned. 1 <= limit <= 50, Default: 50

        # Returns
            **list[Track]**: list of user's top tracks

            **None**: if nothing is found for top tracks *(if status code is `204 (No Content)`)*

        # Raises
            **SpotifyError**: if response status code is anything except `200 (OK)`
        """

        await self._refresh_access_token()

        url = self.BASE_URL + "/me/top/tracks"

        url_params = {
            "limit": limit,
            "time_range": "short_term",  # 4 weeks
        }

        headers = {"Authorization": f"Bearer {self._access_token}"}

        response = await self.session.get(url, params=url_params, headers=headers)

        if response.status not in [204, 200]:
            raise SpotifyError(
                {"status_code": response.status, "message": await response.text()}
            )
        elif response.status == 204:  # 204 (No Content)
            return None

        data_items = (await response.json())["items"]

        tracks: list[Track] = []

        for track_data in data_items:
            track = Track(
                name=track_data["name"],
                album_name=track_data["album"]["name"],
                album_image=track_data["album"]["images"][0]["url"],
                artists=map(format_artists, track_data["artists"]),
                track_url=f"https://open.spotify.com/track/{track_data['uri'].split(':')[2]}",
            )

            tracks.append(track)

        return tracks

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    async def get_top_month_artists(
        self,
        *,  # pydantic keyword only
        limit: Annotated[int, Field(default=10, ge=1, le=50)],
    ) -> list[TopArtist] | None:
        """
        Retrieves user's top artists of the last 4 weeks

        # Parameters
            **limit** (*int*): the limit length of the artists returned. 1 <= limit <= 50, Default: 50

        # Returns
            **list[TopArtist]**: list of user's top artists

            **None**: if nothing is found for top artists *(if status code is `204 (No Content)`)*

        # Raises
            **SpotifyError**: if response status code is anything except `200 (OK)`
        """

        await self._refresh_access_token()

        url = self.BASE_URL + "/me/top/artists"

        url_params = {
            "limit": limit,
            "time_range": "short_term",  # 4 weeks
        }

        headers = {"Authorization": f"Bearer {self._access_token}"}

        response = await self.session.get(url, params=url_params, headers=headers)

        if response.status not in [204, 200]:
            raise SpotifyError(
                {"status_code": response.status, "message": await response.text()}
            )
        elif response.status == 204:  # 204 (No Content)
            return None

        data_items = (await response.json())["items"]

        artists: list[TopArtist] = []

        for data in data_items:
            artist = TopArtist(
                name=data["name"],
                url=f"https://open.spotify.com/artist/{data['uri'].split(':')[2]}",
                image=data["images"][0]["url"],
            )

            artists.append(artist)

        return artists
