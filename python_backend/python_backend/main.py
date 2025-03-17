from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
import aiohttp

from routers import spotify

app = FastAPI()

app.include_router(spotify.router)