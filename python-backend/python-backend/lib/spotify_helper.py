from aiohttp import ClientSession
from pydantic import BaseModel, HttpUrl
from datetime import datetime, timedelta
import asyncio
import base64

from config_helper import Config
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
    name:           str
    artists:        list[str]
    track_url:      HttpUrl
    is_playing:     bool
    album_name:     str
    duration_ms:    int
    progress_ms:    int
    album_image:    HttpUrl

class TopArtist(BaseModel):
    """
    Dataclass representing an artist returned from the spotify's top artists response
    """
    name:   str
    url:    HttpUrl
    image:  HttpUrl

class TopTrack(BaseModel):
    """
    Dataclass representing a track returned from the spotify's top tracks response
    """
    name:           str
    url:            HttpUrl
    artists:        list[str]
    album_image:    HttpUrl

class SpotifyHelper():
    """
    A helper class to interact with the Spotify API.

    Functionality of this class is as follows, refreshing/creating access tokens, fetching the currently playing track,
    fetching the last played track (to be used if there's no currently playing track),
    fetching the top artists of the month, fetching the top tracks of the month.
    """

    BASE_URL: str = "https://api.spotify.com/v1"
    AUTH_URL: str = "https://accounts.spotify.com/api"

    def __init__(self):
        """
        Initializes the SpotifyHelper instance by loading client credentials and setting access token properties.
        """
        self._CLIENT_ID: str = config["spotify"]["client_id"]
        self._CLIENT_SECRET: str = config["spotify"]["client_secret"]
        self._REFRESH_TOKEN: str = config["spotify"]["refresh_token"]

        self._access_token: str = None
        self._expiry_time: datetime = None

    async def _refresh_access_token(self, session: ClientSession):
        """
        Refreshes the Spotify access token if it has expired.

        Args:
            session (ClientSession): An aiohttp client session to make HTTP requests.

        Raises:
            SpotifyError: if response status code is anything except `200 (OK)`
        """

        # check if current token is expired before requesting a new access token
        # so we don't waste a token thats still valid
        now = datetime.now()
        if (self._expiry_time and now <= self._expiry_time):
            return

        url = self.AUTH_URL + "/token"

        basic_auth: str = base64.b64encode(f"{self._CLIENT_ID}:{self._CLIENT_SECRET}".encode()).decode("utf-8")

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "Basic " + basic_auth 
        }

        payload = {
            "grant_type": "refresh_token",
            "refresh_token": self._REFRESH_TOKEN,
        }

        response = await session.post(url, headers=headers, data=payload)

        # Error handling
        if response.status != 200:
            raise SpotifyError({
                "status_code": response.status,
                "error_message": await response.text()
            })

        json_data = await response.json()
        self._access_token = json_data["access_token"]

        # set the expiry to current time + spotify's expires_in
        current_time = datetime.now()
        self._expiry_time = current_time + timedelta(seconds=json_data["expires_in"])
        

    async def get_currently_playing(self, session: ClientSession) -> Track | None:
        """
        Retrieves the currently playing track on the user's Spotify account.

        Args:
            session (ClientSession): An aiohttp client session to make HTTP requests.

        Returns:
            Track: The currently playing track details.

            None: when there's nothing playing

        Raises:
            SpotifyError: if response status code is anything except `200 (OK)`
        """

        # refresh access token
        await self._refresh_access_token(session)

        url = self.BASE_URL + "/me/player/currently-playing"

        headers = {
            "Authorization": f"Bearer {self._access_token}"
        }

        response = await session.get(url, headers=headers)

        # if status code is not 200 or 204 raise exception       
        if response.status not in [200, 204]:
            raise SpotifyError({
                "status_code": response.status,
                "error_message": await response.text()
            })
        
        # 204 (No Content), request was successful but there's no content to be returned
        elif response.status == 204:
            return None
        
        # lambda to be used with map to get only the artist name
        format_artists = lambda artist: artist["name"]
        
        json_data = await response.json()

        currently_playing = Track(
            name=json_data["item"]["name"],
            is_playing=json_data["is_playing"],
            progress_ms=json_data["progress_ms"],
            duration_ms=json_data["item"]["duration_ms"],
            album_name=json_data["item"]["album"]["name"],
            album_image=json_data["item"]["album"]["images"][0]["url"],
            artists= map(format_artists, json_data["item"]["artists"]),
            track_url=f"https://open.spotify.com/track/{json_data["item"]["uri"].split(":")[2]}"
        )

        return currently_playing
        

    async def get_last_played_track(session: ClientSession) -> Track:
        pass

    def get_top_month_artist():
        pass

    def get_top_month_songs():
        pass

async def test():
    async with ClientSession() as session:
        s = SpotifyHelper()
        curr = await s.get_currently_playing(session)
        print(curr)

asyncio.run(test())