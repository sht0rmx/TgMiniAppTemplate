from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.api.routes import apikeys, bot, files, sessions, account, system
from app.api.routes.auth import main as auth
from app.services.caching import cache

api_router = APIRouter()

api_router.include_router(auth.sub_router)
api_router.include_router(account.router)
api_router.include_router(sessions.router)
api_router.include_router(apikeys.router)
api_router.include_router(files.router)
api_router.include_router(bot.router)
api_router.include_router(system.router)

@cache
@api_router.get("/ping", tags=["ping"], summary="Проверка доступности API")
def ping_pong():
    return JSONResponse({"detail": "pong"}, status_code=200)
