from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from pydantic import BaseModel

from .core.logger import setup_logging
from .database import get_database
from .deps import get_config, get_redis
from .integrations import UpstreamError
from .integrations.registry import Integrations
from .routers import all_routers
from .services import db_init_services


@asynccontextmanager
async def lifespan(app: FastAPI):
	setup_logging()
	config = get_config()
	get_redis()  # constructs eagerly so a malformed REDIS_URL fails fast at startup

	# Shared aiohttp session + all third-party API clients, in one typed container.
	integrations = Integrations.create(config)
	app.state.integrations = integrations

	logger.info("Initializing database...")

	db = get_database()
	await db.init()

	# db init services — one connection scope for the whole seeding pass
	async with db.session():
		for service in db_init_services():
			await service(db)

	yield

	await integrations.close()
	await get_redis().aclose()
	await db.close()


config = get_config()

app = FastAPI(root_path="/api", lifespan=lifespan)

# register routers iteratively to avoid circular import issues
for router in all_routers:
	app.include_router(router)

app.add_middleware(
	CORSMiddleware,
	allow_origins=config.api.allowed_origins,
	allow_methods=["*"],
	allow_headers=["*"],
)


@app.exception_handler(UpstreamError)
async def upstream_error_handler(request: Request, exc: UpstreamError) -> JSONResponse:
	"""Single place where third-party API failures become 502 responses."""
	logger.error(f"{exc.service} upstream error mapped to 502: {exc.message}")
	return JSONResponse(
		status_code=502,
		content={"error": type(exc).__name__, "message": exc.message},
	)


class HealthcheckResponse(BaseModel):
	condition: str


@app.get("/healthcheck")
async def healthcheck() -> HealthcheckResponse:
	return HealthcheckResponse(condition="system up")


@app.get("/cv.pdf")
async def get_cv():
	"""Serve the CV PDF file."""
	import os

	from fastapi.responses import FileResponse

	cv_path = os.path.join(os.path.dirname(__file__), "static", "cv.pdf")
	return FileResponse(cv_path, media_type="application/pdf", filename="cv.pdf")
