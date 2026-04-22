import logging
import os

from pathlib import Path
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.utils.translations import run as run_translations
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware
logger = logging.getLogger(__name__)

from app.api.main import api_router
from app.database.database import db_client
from app.database.redis import redis_client
from app.middleware.auth import FingerprintMiddleware
from app.middleware.security import SecurityHeadersMiddleware
from app.middleware.spam import RateLimitMiddleware
from app.services.telegram import telegram_service

load_dotenv()

READY_FILE = Path("/tmp/app_ready")
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


OPENAPI_TAGS = [
    {
        "name": "Auth",
        "description": "Группа маршрутов `/auth` (вложенные теги ниже).",
    },
    {
        "name": "login",
        "description": "Вход: Telegram WebApp, Yandex OAuth, API-ключ бота, QR/коды.",
    },
    {"name": "tokens", "description": "JWT, refresh cookie, recovery, перенос аккаунта."},
    {"name": "check", "description": "Проверка сессии и профиля."},
    {"name": "account", "description": "Привязка/отвязка провайдеров, удаление аккаунта."},
    {"name": "Sessions", "description": "Список устройств и отзыв refresh-сессий."},
    {"name": "API Keys", "description": "Управление API-ключами."},
    {"name": "files", "description": "Загрузка и выдача файлов."},
    {"name": "bot", "description": "Сообщения и действия от имени бота (admin API key)."},
    {"name": "sse", "description": "Server-Sent Events для подтверждения входа с другого устройства."},
    {"name": "ping", "description": "Служебные эндпоинты."},
]


@asynccontextmanager
async def lifespan(_: FastAPI):
    validate_env()

    scheduler.start()

    await redis_client.init()
    await telegram_service.init()

    await db_client.create_db()
    await db_client.seed_admin_key()
    await db_client.clear_db()
    run_translations()
    scheduler.add_job(db_client.clear_db, IntervalTrigger(hours=1))
    scheduler.add_job(run_translations, IntervalTrigger(hours=1))
    READY_FILE.write_text("ok")

    yield

    await telegram_service.close()
    await redis_client.close()
    READY_FILE.unlink(missing_ok=True)
    scheduler.shutdown(wait=False)

app = FastAPI(
    title="TgMiniAppsTemplate Backend",
    description=(
        "API для Telegram Mini App."
    ),
    version="1.0.0",
    openapi_url="/api/v1/openapi.json",
    openapi_tags=OPENAPI_TAGS,
    generate_unique_id_function=custom_generate_unique_id,
    lifespan=lifespan,
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
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
