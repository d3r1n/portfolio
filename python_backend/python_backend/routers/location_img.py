from fastapi import APIRouter, Response

from aiohttp import ClientSession
from contextlib import asynccontextmanager

from python_backend.lib.config_helper import Config

config = Config()
client_session: ClientSession | None = None


@asynccontextmanager
async def lifespan(app: APIRouter):
    global client_session
    client_session = ClientSession()

    yield

    await client_session.close()


router = APIRouter(prefix="/location", lifespan=lifespan)


GEOAPIFY_LONLAT = config["geoapify"]["lonlat"]
GEOAPIFY_APIKEY = config["geoapify"]["api_key"]
GEOAPIFY_URL = f"https://maps.geoapify.com/v1/staticmap?style=osm-liberty&width=600&height=600&center=lonlat:{GEOAPIFY_LONLAT}&zoom=16.5&pitch=43&apiKey={GEOAPIFY_APIKEY}"


# TODO: Add caching
@router.get("/current-location-img", responses={200: {"content": {"image/png": {}}}})
async def current_location_img():
    response = await client_session.get(GEOAPIFY_URL)

    image_bytes = await response.read()

    return Response(image_bytes, media_type="image/png")
