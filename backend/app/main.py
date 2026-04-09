import os
from contextlib import asynccontextmanager

from aiohttp.test_utils import TestClient
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.database.database import db_client
from app.database.redis import redis_client
from app.middleware.auth import FingerprintMiddleware
from app.middleware.security import SecurityHeadersMiddleware
from app.middleware.spam import RateLimitMiddleware
from app.services.telegram import telegram_service

load_dotenv()

REQUIRED_ENV_VARS = [
    "JWT_SECRET",
    "BOT_TOKEN",
    "REFRESH_SECRET",
    "API_SECRET",
    "LOGIN_SECRET",
    "RECOVERY_SECRET",
    "DATABASE_URL",
]


def validate_env():
    missing = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
    if missing:
        raise RuntimeError(
            f"Missing required environment variables: {', '.join(missing)}. "
            "Check your .env file."
        )


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


@asynccontextmanager
async def lifespan(_: FastAPI):
    validate_env()
    await db_client.create_db()
    await db_client.seed_admin_key()
    await db_client.clear_db()
    await redis_client.init()
    await telegram_service.init()
    scheduler.add_job(db_client.clear_db, IntervalTrigger(hours=1))
    scheduler.start()

    yield

    await telegram_service.close()
    await redis_client.close()
    scheduler.shutdown(wait=False)

app = FastAPI(
    title="TgMiniAppsTemplate Backend",
    openapi_url="/api/v1/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
    lifespan=lifespan
)
scheduler = AsyncIOScheduler()


app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Range", "Accept-Ranges"]
)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(FingerprintMiddleware)
app.middleware("http")(RateLimitMiddleware(app, limit=8, period=3))
app.include_router(api_router, prefix="/api/v1")
