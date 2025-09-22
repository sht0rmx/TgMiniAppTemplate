from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from modules.db.engine import Database
from modules.routers.v1.UserRouter import user_router
from modules.routers.v1.TokenRouter import token_router

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
    "http://127.0.0.1:5173",
    "http://localhost:5173",
    "http://192.168.31.184:5173",
    "https://miniapp.snipla.ru",
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
app.include_router(token_router)
