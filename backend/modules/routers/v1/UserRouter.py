from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from decouple import config

from modules.db.engine import Database
from modules.services.UsersService import UsersService
from modules.schemes.user.CheckUserDto import UserDto

user_router = APIRouter(prefix="/telegram/auth", tags=["auth"])
security = HTTPBearer()
user_service = UsersService()
db_dep = Database()


@user_router.post("/webapp")
async def tg_webapp_auth(dto: UserDto, db: AsyncSession = Depends(db_dep.get_session)):
    bot_token: str = str(config("BOT_TOKEN"))

    params = dict(x.split("=", 1) for x in dto.initData.split("&") if "=" in x)
    hash_str = params.pop("hash", None)

    if not hash_str or not user_service.check_telegram_auth(hash_str, dto.initData, bot_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Telegram initData",
        )

    telegram_id = int(params.get("id", 0))
    username = params.get("username", "")
    firstname = params.get("first_name", "")
    photo = params.get("photo_url")

    user = await user_service.curid_user(db, dto, telegram_id, username, firstname, photo)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Invalid Telegram initData",
        )
    
    return {
        "id": user.id,
        "telegram_id": user.telegram_id,
        "username": user.username,
        "token": user.token_key,
    }


@user_router.post("/bot")
async def bot_admin_auth(
    creds: HTTPAuthorizationCredentials = Depends(security),
):
    if not user_service.check_admin_token(creds.credentials):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API token",
        )

    return {"status": "ok"}
