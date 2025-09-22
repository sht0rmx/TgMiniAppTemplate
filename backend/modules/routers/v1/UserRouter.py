from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from decouple import config

from dependencies.auth import jwt_required
from modules.db.models.User import User
from modules.db.engine import Database
from modules.services.UsersService import UsersService
from modules.schemes.user.CheckUserDto import UserDto

user_router = APIRouter(prefix="/telegram/auth", tags=["auth"])
security = HTTPBearer()
user_service = UsersService()
db_dep = Database()



@user_router.post("/webapp")
async def tg_webapp_auth(
    dto: UserDto,
    request: Request,
    db: AsyncSession = Depends(db_dep.get_session),
):
    bot_token: str = str(config("BOT_TOKEN"))

    params = user_service.parse_init_data(init_data=dto.initData)
    hash_str = params.pop("hash", None)

    if not hash_str or not user_service.check_telegram_auth(hash_str, dto.initData, bot_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Telegram initData",
        )

    user_info = params.get("user", {})
    telegram_id = int(user_info.get("id", 0))
    username = user_info.get("username", "")
    firstname = user_info.get("first_name", "")
    photo = user_info.get("photo_url")

    device_id = request.headers.get("User-Agent", "web")
    ip_address = request.client.host if request.client else "0.0.0.0"

    result = await user_service.curid_user(
        db,
        telegram_id=telegram_id,
        username=username,
        firstname=firstname,
        photo=photo,
        device_id=device_id,
        ip_address=ip_address,
    )

    user = result["user"]
    tokens = result["tokens"]

    return {
        "user": {
            "id": str(user.id),
            "telegram_id": user.telegram_id,
            "username": user.username,
            "name": user.name,
            "avatar_url": user.avatar_url,
        },
        "tokens": tokens
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


@user_router.get("/profile")
async def get_profile(
    db: AsyncSession = Depends(db_dep.get_session),
    payload: dict = Depends(jwt_required)
):
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    query = await db.execute(select(User).where(User.telegram_id == int(user_id)))
    user = query.scalar()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": str(user.id),
        "telegram_id": user.telegram_id,
        "username": user.username,
        "name": user.name,
        "avatar_url": user.avatar_url,
    }