from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .deps import get_client_session, get_config
from .routers import books, spotify


@asynccontextmanager
async def lifespan(app: FastAPI):
	await get_client_session.init()

	yield

	await get_client_session.close()


config = get_config()

app = FastAPI(root_path="/api", lifespan=lifespan)

app.include_router(spotify.router)
app.include_router(books.router)

app.add_middleware(
	CORSMiddleware,
	allow_origins=config.api.allowed_origins,
	allow_methods=["*"],
	allow_headers=["*"],
)


@app.get("/healthcheck")
async def healthcheck():
	# TODO: implement proper healthcheck
	return JSONResponse({"condition": "system up"}, status_code=200)
