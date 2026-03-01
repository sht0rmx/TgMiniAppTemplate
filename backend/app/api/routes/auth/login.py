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
from app.middleware.auth import deny_bot, require_origin
from app.services.auth.AuthService import AuthUtils
from app.services.telegram import telegram_service
from app.schemas.models import User, WebAppLoginRequest
from app.utils import create_hash, gen_code, parse_expire

logger = logging.getLogger("uvicorn.error")

router = APIRouter(prefix="/login", tags=["login"])


@router.post("/webapp", dependencies=[Depends(require_origin)])
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

    # Generate recovery code for new users and send via Telegram
    if is_new:
        asyncio.create_task(
            _send_recovery_for_new_user(
                user_id=str(user.id), telegram_id=user_data.id
            )
        )

    resp = JSONResponse(content={"access_token": access_token}, status_code=200)

    resp.set_cookie(
        key="refresh_token",
        value=str(refresh_token),
        httponly=True,
        max_age=int(parse_expire(os.getenv("REFRESH_EXPIRE", "60d")).total_seconds()),
        secure=not bool(os.getenv("DEV", "")),
        samesite="lax",
    )

    return resp


async def _send_recovery_for_new_user(user_id: str, telegram_id: int):
    try:
        code = gen_code(length=16)
        await db_client.create_recovery_code(user_id=user_id, code=code)
        await telegram_service.send_recovery_code(chat_id=telegram_id, code=code)
        logger.info(f"Recovery code sent to telegram_id={telegram_id}")
    except AlreadyCreated:
        logger.warning(f"Recovery code already exists for user {user_id}")
    except Exception as e:
        logger.error(f"Failed to send recovery code to {telegram_id}: {e}")


@router.get("/api-key")
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


@router.get("/getqr", dependencies=[Depends(require_origin)])
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


@router.get("/code/search/{code}", dependencies=[Depends(require_origin), Depends(deny_bot())])
async def search_by_code(code: str):
    try:
        await db_client.get_login_session(code=code)
        return JSONResponse({"detail": "Login found"}, status_code=200)
    except (NotFound, Expired):
        return JSONResponse({"detail": "Login code not found or expired"}, status_code=400)


@router.get("/code/accept/{code}", dependencies=[Depends(require_origin), Depends(deny_bot())])
async def accept_by_code(request: Request, code: str):
    user_id = request.state.user_id
    role = request.state.role

    if not user_id:
        return JSONResponse({"detail": "Missing user_id"}, status_code=400)

    try:
        await db_client.accept_login(code=code, user_id=user_id, role=role)
        return JSONResponse({"detail": "OK!"}, status_code=200)
    except (NotFound, Expired):
        return JSONResponse({"detail": "Login code not found or expired"}, status_code=400)


@router.get("/search/{loginid}", dependencies=[Depends(require_origin), Depends(deny_bot())])
async def check_login(loginid: str):
    try:
        await db_client.get_login_session(login_hash=loginid)
        return JSONResponse({"detail": "Login found"}, status_code=200)
    except (NotFound, Expired):
        return JSONResponse({"detail": "Login not founded"}, status_code=400)


@router.get("/accept/{loginid}", dependencies=[Depends(require_origin), Depends(deny_bot())])
async def validate_login(request: Request, loginid: str):
    user_id = request.state.user_id
    role = request.state.role

    if not user_id:
        return JSONResponse({"detail": "Missing user_id"}, status_code=400)

    try:
        await db_client.accept_login(login=loginid, user_id=user_id, role=role)
        return JSONResponse({"detail": "OK!"}, status_code=200)
    except (NotFound, Expired):
        return JSONResponse({"detail": "Login not founded"}, status_code=400)
