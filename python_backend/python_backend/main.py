from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from python_backend.routers import location, spotify
from python_backend.lib.config_helper import Config

config = Config()

app = FastAPI()

app.include_router(spotify.router)
app.include_router(location.router)

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
