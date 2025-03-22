from fastapi import FastAPI
from fastapi.responses import JSONResponse

from python_backend.routers import spotify

app = FastAPI()

app.include_router(spotify.router)

@app.get("/healthcheck")
async def healthcheck():
    # TODO: implement proper healthcheck
    return JSONResponse(
        {
            "condition": "UP"
        },
        status_code=200
    )