from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from python_backend.routers import spotify, location_img


app = FastAPI()

app.include_router(spotify.router)
app.include_router(location_img.router)

allowed_origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthcheck")
async def healthcheck():
    # TODO: implement proper healthcheck
    return JSONResponse({"condition": "UP"}, status_code=200)
