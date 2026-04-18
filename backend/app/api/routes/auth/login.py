import asyncio
import json
import logging
import os
import time
import uuid
from urllib.parse import parse_qs

from fastapi import APIRouter, Depends, Header, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.database.database import AlreadyCreated, Expired, NotFound, db_client
from app.middleware.auth import deny_bot
from app.middleware.spam import rate_limit
from app.schemas.models import User, WebAppLoginRequest, YandexLoginRequest
from app.services.auth.AuthService import AuthUtils, auth_service
from app.services.auth.YandexOAuthService import YandexOAuthService
from app.services.telegram import telegram_service
from app.utils import create_hash, gen_code, parse_expire

logger = logging.getLogger("uvicorn.error")

router = APIRouter(prefix="/login", tags=["login"])


@rate_limit(limit=5, period=60)
@router.post(
    "/webapp",
    dependencies=[],
    summary="Вход через Telegram WebApp",
    description="Проверяет `initData`, создаёт или обновляет пользователя и выдаёт access/refresh токены.",
)
async def webapp_login(
    request_data: WebAppLoginRequest,
    request: Request,
    user_agent: str = Header(default=""),
):
    parsed = {k: v[0] for k, v in parse_qs(request_data.initData).items()}

    if not parsed.get("auth_date", None):
        return JSONResponse({"detail": "authdate not founded"}, status_code=401)

    auth_time = parsed["auth_date"]
    current_time = int(time.time())

    if abs(current_time - int(auth_time)) >= (5 * 60):
        return JSONResponse({"detail": "authdate so old! max 5min"}, status_code=401)

    try:
        user_data = User(**json.loads(parsed["user"]))
    except ValidationError:
        return JSONResponse({"detail": "InitData havent right format"}, status_code=401)

    if not AuthUtils.check_initdata(
        initdata=request_data.initData, hash_str=parsed["hash"]
    ):
        return JSONResponse({"detail": "InitData validation failed"}, status_code=401)

    user, is_new = await db_client.update_user(
        telegram_id=user_data.id,
        username=user_data.username,
        name=f"{user_data.first_name} {user_data.last_name}",
        avatar_url=user_data.photo_url,
    )

    await db_client.link_user_telegram(str(user.id), user_data.id)

    fingerprint = request.state.fingerprint
    if not fingerprint:
        return JSONResponse({"detail": "Missing fingerprint"}, status_code=400)

    ip = request.client.host if request.client else "127.0.0.1"

    refresh_token = str(uuid.uuid4())

    session = await db_client.create_refresh_session(
        refresh_token=refresh_token,
        fingerprint=fingerprint,
        ip=ip,
        user_id=str(user.id),
        user_agent=user_agent,
    )

    access_token = AuthUtils.gen_jwt_token(
        user_id=user.id, session_id=session.id, role=str(user.role)
    )

    recovery_code = None
    if is_new:
        try:
            code = gen_code(length=16)
            await db_client.create_recovery_code(user_id=str(user.id), code=code)
            recovery_code = code
            asyncio.create_task(
                _send_recovery_for_new_user(
                    user_id=str(user.id), telegram_id=user_data.id, code=code
                )
            )
        except AlreadyCreated:
            pass

    return auth_service.json_with_refresh_cookie(
        access_token=access_token,
        refresh_token=refresh_token,
        recovery_code=recovery_code,
        cookie_samesite="lax",
    )


async def _send_recovery_for_new_user(user_id: str, telegram_id: int, code: str):
    try:
        await telegram_service.send_recovery_code(chat_id=telegram_id, code=code)
        logger.info("Recovery code sent to telegram_id=%s", telegram_id)
    except Exception as e:
        logger.error("Failed to send recovery code to %s: %s", telegram_id, e)


@router.get(
    "/api-key",
    summary="Вход по API-ключу (бот)",
    description="Обмен `Bearer sk_...` на JWT с метаданными бота.",
)
async def bot_login(request: Request):
    auth = request.headers.get("authorization", "default").strip()

    if not auth.startswith("Bearer"):
        return JSONResponse(
            {"detail": "Auth header must starts with `Bearer`"}, status_code=401
        )

    token = auth.split(" ")[1]

    if not token.startswith("sk_"):
        return JSONResponse(
            {"detail": "Api key must starts with `sk_`"}, status_code=401
        )

    key_hash = create_hash("API_SECRET", token)

    try:
        api_key = await db_client.get_api_key(hash=str(key_hash))
    except NotFound:
        return JSONResponse({"detail": "Api key not founded"}, status_code=401)

    user = await db_client.get_user(uid=str(api_key.user_id))
    access_token = AuthUtils.gen_jwt_token(
        user_id=user.id, session_id=api_key.id, role=str(user.role), is_bot=True
    )

    user_entity = {
        "id": str(user.id),
        "telegram_id": user.telegram_id,
        "username": user.username,
        "name": user.name,
        "role": user.role,
        "avatar_url": user.avatar_url,
        "last_seen": user.last_seen.isoformat(),
        "created_at": user.created_at.isoformat(),
    }

    return JSONResponse(
        content={"access_token": access_token, "user": user_entity}, status_code=200
    )


@rate_limit(limit=5, period=60)
@router.get(
    "/getqr",
    dependencies=[],
    summary="QR / одноразовый код для входа с другого устройства",
)
async def get_qr_code(request: Request):
    fingerprint = request.state.fingerprint
    if not fingerprint:
        return JSONResponse({"detail": "Missing fingerprint"}, status_code=400)

    code = gen_code(length=8)
    ip = request.client.host if request.client else "127.0.0.1"
    login_id, login_code = await db_client.create_login_session(
        code=code, fingerprint=fingerprint, ip=ip
    )

    return JSONResponse({"login_id": login_id, "code": login_code}, status_code=200)


@rate_limit(limit=5, period=60)
@router.get(
    "/code/search/{code}",
    dependencies=[Depends(deny_bot)],
    summary="Проверить код входа",
)
async def search_by_code(code: str):
    try:
        await db_client.get_login_session(code=code)
        return JSONResponse({"detail": "Login found"}, status_code=200)
    except (NotFound, Expired):
        return JSONResponse({"detail": "Login code not found or expired"}, status_code=400)


@rate_limit(limit=5, period=60)
@router.get(
    "/code/accept/{code}",
    dependencies=[Depends(deny_bot)],
    summary="Подтвердить вход по коду",
)
async def accept_by_code(request: Request, code: str):
    user_id = request.state.user_id
    role = request.state.role

    if not user_id:
        return JSONResponse({"detail": "Missing user_id"}, status_code=400)

    try:
        await auth_service.accept_login(code=code, user_id=user_id, role=role)
        return JSONResponse({"detail": "OK!"}, status_code=200)
    except (NotFound, Expired):
        return JSONResponse({"detail": "Login code not found or expired"}, status_code=400)


@router.get(
    "/search/{loginid}",
    dependencies=[Depends(deny_bot)],
    summary="Проверить сессию по login_id",
)
async def check_login(loginid: str):
    try:
        login_hash = create_hash("LOGIN_SECRET", str(loginid))
        await db_client.get_login_session(login_hash=login_hash)
        return JSONResponse({"detail": "Login found"}, status_code=200)
    except (NotFound, Expired):
        return JSONResponse({"detail": "Login not founded"}, status_code=400)


@router.get(
    "/accept/{loginid}",
    dependencies=[Depends(deny_bot)],
    summary="Подтвердить вход по login_id",
)
async def validate_login(request: Request, loginid: str):
    user_id = request.state.user_id
    role = request.state.role

    if not user_id:
        return JSONResponse({"detail": "Missing user_id"}, status_code=400)

    try:
        await auth_service.accept_login(login=loginid, user_id=user_id, role=role)
        return JSONResponse({"detail": "OK!"}, status_code=200)
    except (NotFound, Expired):
        return JSONResponse({"detail": "Login not founded"}, status_code=400)


@rate_limit(limit=5, period=60)
@router.post(
    "/yandex",
    dependencies=[],
    summary="Вход через Yandex OAuth",
)
async def yandex_login(
    request_data: YandexLoginRequest,
    request: Request,
    user_agent: str = Header(default=""),
):
    code = request_data.code
    if not code:
        return JSONResponse({"detail": "Missing authorization code"}, status_code=400)

    try:
        oauth_service = YandexOAuthService()
    except ValueError as e:
        logger.error("Yandex OAuth configuration error: %s", e)
        return JSONResponse(
            {"detail": "OAuth service not configured"}, status_code=500
        )

    try:
        auth_result = await oauth_service.authenticate_user(code)
        if not auth_result:
            return JSONResponse(
                {"detail": "Failed to authenticate with Yandex"}, status_code=401
            )

        profile = YandexOAuthService.parse_profile(auth_result["user_info"])
        yandex_id = profile["yandex_id"]
        if not yandex_id:
            return JSONResponse({"detail": "Invalid Yandex response"}, status_code=400)

        user, is_new = await db_client.find_or_create_yandex_user(
            yandex_id=yandex_id,
            username=profile["username"],
            name=profile["name"],
            avatar_url=profile["avatar_url"],
            email=profile["email"],
        )
        await db_client.link_user_yandex(str(user.id), yandex_id)

        fingerprint = request.state.fingerprint
        if not fingerprint:
            return JSONResponse({"detail": "Missing fingerprint"}, status_code=400)

        ip = request.client.host if request.client else "127.0.0.1"
        refresh_token = str(uuid.uuid4())

        session = await db_client.create_refresh_session(
            refresh_token=refresh_token,
            fingerprint=fingerprint,
            ip=ip,
            user_id=str(user.id),
            user_agent=user_agent,
        )

        access_token = AuthUtils.gen_jwt_token(
            user_id=user.id, session_id=session.id, role=str(user.role)
        )

        recovery_code = None
        if is_new:
            try:
                rec = gen_code(length=16)
                await db_client.create_recovery_code(user_id=str(user.id), code=rec)
                recovery_code = rec
            except AlreadyCreated:
                pass

        return auth_service.json_with_refresh_cookie(
            access_token=access_token,
            refresh_token=refresh_token,
            recovery_code=recovery_code,
            cookie_samesite="none",
            cookie_path="/",
        )

    except Exception as e:
        logger.error("Error during Yandex OAuth login: %s", e)
        return JSONResponse({"detail": "Internal server error"}, status_code=500)
