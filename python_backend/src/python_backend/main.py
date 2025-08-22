from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from python_backend.lib.config import Config
from python_backend.routers import books, spotify

from .dependencies import CLIENT_SESSION

config = Config()


@asynccontextmanager
async def lifespan(app: FastAPI):
	CLIENT_SESSION.startup()

	yield

	await CLIENT_SESSION.shutdown()


app = FastAPI(root_path="/api", lifespan=lifespan)

app.include_router(spotify.router)
app.include_router(books.router)

app.add_middleware(
	CORSMiddleware,
	allow_origins=config["api"]["allowed_origins"],
	allow_methods=["*"],
	allow_headers=["*"],
)


@app.get("/healthcheck")
async def healthcheck():
	# TODO: implement proper healthcheck
	return JSONResponse({"condition": "system up"}, status_code=200)
