"""Client parsing tests with canned upstream payloads (no network)."""

import pytest

from portfolio.core.config import load_config
from portfolio.integrations.hardcover.client import HardcoverApi, HardcoverError
from portfolio.integrations.openweather.client import OpenWeatherApi, WeatherError
from portfolio.integrations.spotify.client import SpotifyApi, SpotifyError

from .fakes import FakeResponse, FakeSession

TOKEN_RESPONSE = FakeResponse(json_data={"access_token": "tok", "expires_in": 3600})

SPOTIFY_TRACK_ITEM = {
	"name": "Song",
	"uri": "spotify:track:abc123",
	"album": {"name": "Album", "images": [{"url": "https://img.example/a.jpg"}]},
	"artists": [{"name": "Artist One"}, {"name": "Artist Two"}],
	"duration_ms": 200000,
}


async def test_spotify_currently_playing():
	session = FakeSession(
		get_responses=[
			FakeResponse(json_data={"item": SPOTIFY_TRACK_ITEM, "is_playing": True, "progress_ms": 1234}),
		],
		post_response=TOKEN_RESPONSE,
	)
	api = SpotifyApi(load_config(), session)  # pyright: ignore[reportArgumentType]

	track = await api.get_currently_playing()

	assert track is not None
	assert track.name == "Song"
	assert track.artists == ["Artist One", "Artist Two"]
	assert str(track.track_url) == "https://open.spotify.com/track/abc123"
	assert track.is_playing is True
	assert track.progress_ms == 1234
	assert track.duration_ms == 200000


async def test_spotify_204_means_none():
	session = FakeSession(get_responses=[FakeResponse(status=204)], post_response=TOKEN_RESPONSE)
	api = SpotifyApi(load_config(), session)  # pyright: ignore[reportArgumentType]

	assert await api.get_currently_playing() is None


async def test_spotify_error_carries_status():
	session = FakeSession(get_responses=[FakeResponse(status=500, text="boom")], post_response=TOKEN_RESPONSE)
	api = SpotifyApi(load_config(), session)  # pyright: ignore[reportArgumentType]

	with pytest.raises(SpotifyError) as exc_info:
		await api.get_last_played_track()
	assert exc_info.value.status_code == 500
	assert exc_info.value.message == "boom"


HARDCOVER_PAYLOAD = {
	"data": {
		"me": [
			{
				"user_books": [
					{
						"book": {
							"title": "The Book",
							"slug": "the-book",
							"pages": 320,
							"image": {"url": "https://img.example/b.jpg", "color": "#112233"},
							"contributions": [{"author": {"name": "Author A"}}, {"author": {"name": "Author B"}}],
						},
						"user_book_reads": [{"progress": 0.42}],
					}
				]
			}
		]
	}
}


async def test_hardcover_parses_book():
	session = FakeSession(post_response=FakeResponse(json_data=HARDCOVER_PAYLOAD))
	api = HardcoverApi(load_config(), session)  # pyright: ignore[reportArgumentType]

	book = await api.get_currently_reading_book()

	assert book is not None
	assert book.title == "The Book"
	assert book.author == "Author A, Author B"
	assert book.pages == 320
	assert book.progress == pytest.approx(42.0)  # 0-1 fraction is normalized to percent
	assert str(book.link) == "https://hardcover.app/books/the-book"
	assert book.image_dominant_color == "#112233"


async def test_hardcover_no_books_means_none():
	session = FakeSession(post_response=FakeResponse(json_data={"data": {"me": [{"user_books": []}]}}))
	api = HardcoverApi(load_config(), session)  # pyright: ignore[reportArgumentType]

	assert await api.get_currently_reading_book() is None


async def test_hardcover_graphql_error_raises():
	session = FakeSession(post_response=FakeResponse(json_data={"errors": [{"message": "bad token"}]}))
	api = HardcoverApi(load_config(), session)  # pyright: ignore[reportArgumentType]

	with pytest.raises(HardcoverError) as exc_info:
		await api.get_currently_reading_book()
	assert exc_info.value.message == "bad token"


WEATHER_PAYLOAD = {
	"weather": [{"main": "Clouds", "description": "overcast clouds", "icon": "04d"}],
	"main": {"temp": 18.5, "feels_like": 18.0, "humidity": 77},
	"wind": {"speed": 3.6},
}


async def test_openweather_parses_current_weather():
	session = FakeSession(get_responses=[FakeResponse(json_data=WEATHER_PAYLOAD)])
	api = OpenWeatherApi(load_config(), session)  # pyright: ignore[reportArgumentType]

	weather = await api.get_current_weather(latitude=45.9, longitude=-64.4)

	assert weather is not None
	assert weather.condition == "Clouds"
	assert weather.temperature == 18.5
	assert weather.wind_speed == 3.6


async def test_openweather_malformed_payload_raises():
	session = FakeSession(get_responses=[FakeResponse(json_data={"unexpected": "shape"})])
	api = OpenWeatherApi(load_config(), session)  # pyright: ignore[reportArgumentType]

	with pytest.raises(WeatherError):
		await api.get_current_weather(latitude=0, longitude=0)


async def test_openweather_geocoding():
	session = FakeSession(
		get_responses=[FakeResponse(json_data=[{"name": "Sackville", "lat": 45.9, "lon": -64.4, "country": "CA"}])]
	)
	api = OpenWeatherApi(load_config(), session)  # pyright: ignore[reportArgumentType]

	geo = await api.get_coordinates_from_location_name("Sackville, Canada")

	assert geo is not None
	assert (geo.lat, geo.lon) == (45.9, -64.4)
