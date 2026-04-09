import logging
import os
import uuid

from fastapi import APIRouter, Cookie, Depends, Header, Request
from fastapi.responses import JSONResponse

from app.database.database import AlreadyCreated, Expired, NotFound, Revoked, db_client
from app.middleware.auth import deny_bot, require_auth, require_origin
from app.middleware.spam import rate_limit
from app.services.auth.AuthService import AuthUtils
from app.services.telegram import telegram_service
from app.schemas.models import RecoveryRequest
from app.utils import gen_code, parse_expire

logger = logging.getLogger("uvicorn.error")


router = APIRouter(prefix="/token", tags=["tokens"])


# recreate session token
@router.get(
    "/recreate-tokens", dependencies=[Depends(require_origin), Depends(deny_bot), Depends(require_auth)]
)
async def get_refresh_token(request: Request, user_agent: str = Header(default="")):
    if not hasattr(request.state, "fingerprint") or not hasattr(request.state, "user_id"):
        return JSONResponse(
            {"detail": "Missing fingerprint or user_id"}, status_code=400
        )

    fingerprint = request.state.fingerprint
    user_id = request.state.user_id

    ip = request.client.host if request.client else "127.0.0.1"
    refresh_token = str(uuid.uuid4())

    session = await db_client.create_refresh_session(
        refresh_token=refresh_token,
        fingerprint=fingerprint,
        ip=ip,
        user_agent=user_agent,
        user_id=user_id,
    )

    access_token = AuthUtils.gen_jwt_token(
        user_id=request.state.user_id,
        session_id=session.id,
        role=str(request.state.role),
    )
    resp = JSONResponse(content={"access_token": access_token}, status_code=200)

    resp.set_cookie(
        key="refresh_token",
        value=str(refresh_token),
        httponly=True,
        max_age=int(parse_expire(os.getenv("REFRESH_EXPIRE", "60d")).total_seconds()),
        secure=not bool(os.getenv("DEV", "")),
        samesite="lax",
        path="/"
    )

    return resp


# get jwt and update session token
@rate_limit(limit=10, period=60)  # 10 token refreshes per 60s
@router.get("/get-tokens", dependencies=[Depends(require_origin)])
async def get_access_token(request: Request, refresh_token: str | None = Cookie(default=None),):
    if not hasattr(request.state, "fingerprint"):
        return JSONResponse({"detail": "Missing fingerprint"}, status_code=400)

    fingerprint = request.state.fingerprint

    if not refresh_token:
        return JSONResponse(
            {
                "detail": "Missing refresh token, make auth by /api/v1/auth/login /webapp or /api-key"
            },
            status_code=400,
        )

    ip = request.client.host if request.client else "127.0.0.1"

    try:
        new_refresh_token = str(uuid.uuid4())
        session = await db_client.update_refresh_session(
            fingerprint=fingerprint, ip=ip, rt_key=refresh_token, new_rt_key=new_refresh_token
        )

        user = await db_client.get_user(uid=str(session.user_id))

        access_token = AuthUtils.gen_jwt_token(
            user_id=user.id, session_id=session.id, role=str(user.role)
        )
        resp = JSONResponse(content={"access_token": access_token}, status_code=200)

        resp.set_cookie(
            key="refresh_token",
            value=new_refresh_token,
            httponly=True,
            max_age=int(parse_expire(os.getenv("REFRESH_EXPIRE", "60d")).total_seconds()),
            secure=not bool(os.getenv("DEV", "")),
            samesite="lax",
            path="/",
        )

        return resp
    except (NotFound, Revoked, Expired):
        return JSONResponse(
            {
                "detail": "Missing refresh token, make auth by /api/v1/auth/login /webapp or /api-key"
            },
            status_code=400,
        )


# revoke refresh session
@router.get("/revoke", dependencies=[Depends(require_origin), Depends(deny_bot())])
async def revoke_resresh_session(request: Request):
    if not hasattr(request.state, "fingerprint"):
        return JSONResponse({"detail": "Missing fingerprint"}, status_code=400)

    fingerprint = request.state.fingerprint

    await db_client.revoke_refresh_session(fingerprint=fingerprint, revoked=True)

    return JSONResponse(
        content={"detail": "Token successfully revoked"}, status_code=200
    )


# generate recovery code
@rate_limit(limit=3, period=300)  # 3 recovery attempts per 5min
@router.get("/recovery", dependencies=[Depends(require_origin), Depends(require_auth)])
async def generate_recovery(request: Request):
    if not hasattr(request.state, "user_id"):
        return JSONResponse({"detail": "Missing user_id"}, status_code=400)

    user_id = request.state.user_id

    try:
        code = gen_code(length=16)
        await db_client.create_recovery_code(user_id=user_id, code=code)

        # Send recovery code to user's Telegram chat
        sent = False
        try:
            user = await db_client.get_user(uid=user_id)
            sent = await telegram_service.send_recovery_code(
                chat_id=user.telegram_id, code=code
            )
        except NotFound:
            logger.warning(f"User {user_id} not found for recovery notification")
        except Exception as e:
            logger.error(f"Failed to send recovery code via Telegram: {e}")

        if not sent:
            return JSONResponse(
                content={"code": code, "detail": "Code generated, but failed to send via Telegram"},
                status_code=200,
            )

        return JSONResponse(content={"detail": "Recovery code sent to your Telegram"}, status_code=200)
    except AlreadyCreated:
        return JSONResponse(
            content={"detail": "Code already generated"}, status_code=400
        )


# transfer user
@rate_limit(limit=3, period=300)
@router.post("/transfer", dependencies=[Depends(require_origin), Depends(deny_bot()), Depends(require_auth)])
async def transfer_user(request_data: RecoveryRequest, request: Request):
    if not hasattr(request.state, "user_id"):
        return JSONResponse({"detail": "Missing user_id"}, status_code=400)

    user_id = request.state.user_id
    try:
        user = await db_client.get_user(uid=user_id)
        if not user.telegram_id and not user.yandex_id:
            return JSONResponse(
                {"detail": "Account transfer requires authentication via Telegram or Yandex"},
                status_code=403,
            )
    except NotFound:
        return JSONResponse({"detail": "User not found"}, status_code=404)

    try:
        await db_client.recovery_user(code=request_data.recovery_code, user_id=user_id)
        return JSONResponse(content={"detail": "Transfer successfull"}, status_code=200)
    except NotFound as e:
        logger.error(f"Recovery failed: code={request_data.recovery_code}, current_user={user_id}, error={e}")
        return JSONResponse(
            content={"detail": "Recovery failed, user or recovery code not found"},
            status_code=400,
        )
