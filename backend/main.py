from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from modules.db.engine import Database
from modules.routers.v1.UserRouter import user_router

version = "v0.0.1"

description = """
Backend part of https://github.com/sht0rmx/TgMiniAppTemplate
"""


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = Database()
    await db.create_db()
    yield
    print("Server is stopping")


app = FastAPI(
    title="Admin panel",
    description=description,
    lifespan=lifespan,
    version=version,
)

origins = [
    "http://127.0.0.1:8080",
    "http://localhost:8080",
    "https://jlj73h8b-8080.euw.devtunnels.ms/",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/ping")
async def root():
    return {"ping": "pong"}


app.include_router(user_router)
