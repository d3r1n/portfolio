from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from pydantic import BaseModel

from .deps import get_client_session, get_config
from .lib.database import init_db
from .lib.util.logger import setup_logging
from .routers import auth_router, books_router, projects_router, spotify_router


@asynccontextmanager
async def lifespan(app: FastAPI):
	await get_client_session.init()
	setup_logging()

	logger.info("Initializing database...")

	await init_db()

	yield

	await get_client_session.close()


config = get_config()

app = FastAPI(root_path="/api", lifespan=lifespan)

app.include_router(books_router)
app.include_router(projects_router)
app.include_router(spotify_router)
app.include_router(auth_router)

app.add_middleware(
	CORSMiddleware,
	allow_origins=config.api.allowed_origins,
	allow_methods=["*"],
	allow_headers=["*"],
)


class HealthcheckResponse(BaseModel):
	condition: str


@app.get("/healthcheck")
async def healthcheck() -> HealthcheckResponse:
	return HealthcheckResponse(condition="system up")
