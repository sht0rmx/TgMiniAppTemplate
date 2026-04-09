import os

import jwt
from fastapi import Depends, HTTPException, Request, WebSocket
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.middleware.base import BaseHTTPMiddleware


from app.database.database import Banned, Expired, NotFound, Revoked, db_client
from app.services.auth.AuthService import AuthUtils
from app.utils import create_hash

bearer_scheme = HTTPBearer()

async def require_auth(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(401, "Invalid authorization scheme")

    raw_token = credentials.credentials

    # ---- API KEY FLOW ----
    if raw_token.startswith("sk_"):
        key_hash = create_hash("API_SECRET", raw_token)

        try:
            api_key = await db_client.get_api_key(hash=str(key_hash))
        except (NotFound, Banned):
            raise HTTPException(401, "Invalid API key")

        user = await db_client.get_user(uid=str(api_key.user_id))

        token = AuthUtils.gen_jwt_token(
            user_id=user.id,
            session_id=api_key.id,
            role=str(user.role),
            is_bot=True,
        )
    else:
        token = raw_token

    # ---- JWT VALIDATION ----
    try:
        payload = jwt.decode(
            token,
            os.getenv("JWT_SECRET"),
            algorithms=[os.getenv("JWT_ALG", "HS256")],
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid token")

    if not payload.get("sub") or not payload.get("sid"):
        raise HTTPException(401, "Malformed token")

    # ---- METADATA CHECK ----
    if payload.get("is_bot"):
        try:
            await db_client.get_api_key(api_key_id=payload["sid"])
        except (NotFound, Banned):
            raise HTTPException(401, "Invalid API key metadata")
    else:
        fingerprint = request.state.fingerprint
        if not fingerprint:
            raise HTTPException(401, "Missing fingerprint")

        try:
            await db_client.get_refresh_session(
                fingerprint=fingerprint,
                session_id=payload["sid"],
            )
        except (NotFound, Expired, Revoked):
            raise HTTPException(401, "Invalid session metadata")

    request.state.user_id = payload["sub"]
    request.state.role = payload.get("role")
    request.state.session_id = payload["sid"]

    return payload


async def websocket_auth(ws: WebSocket):
    auth = ws.headers.get("authorization")
    if not auth or not auth.startswith("Bearer "):
        await ws.close(code=1008)
        raise HTTPException(401, "Missing or invalid Authorization header")

    token = auth.split(" ")[1]
    try:
        payload = jwt.decode(
            token,
            os.getenv("JWT_SECRET"),
            algorithms=[os.getenv("JWT_ALG", "HS256")]
        )
    except jwt.ExpiredSignatureError:
        await ws.close(code=1008)
        raise HTTPException(401, "Token expired")
    except jwt.InvalidTokenError:
        await ws.close(code=1008)
        raise HTTPException(401, "Invalid token")

    if not payload.get("is_bot"):
        await ws.close(code=1008)
        raise HTTPException(401, "Connection as user")

    try:
        await db_client.get_api_key(api_key_id=payload.get("sid"))
    except (NotFound, Banned):
        await ws.close(code=1008)
        raise HTTPException(401, "Invalid API key")

    if payload.get("role") != "admin":
        await ws.close(code=1008)
        raise HTTPException(401, "Connection denied")

    return payload


def require_admin():
    def _check(payload=Depends(require_auth)):
        if payload.get("role") != "admin":
            raise HTTPException(403, "Access denied")
        return payload
    return _check


def deny_bot():
    def _check(payload=Depends(require_auth)):
        if payload.get("is_bot"):
            raise HTTPException(403, "Access denied")
        return payload
    return _check


def require_origin(request: Request):
    allowed = os.getenv("CORS_ORIGINS", "").split(",")
    origin = request.headers.get("origin")
    if origin and origin not in allowed:
        raise HTTPException(403, "Origin not allowed")


class FingerprintMiddleware(BaseHTTPMiddleware):
    FINGERPRINT_MIN_LEN = 16
    FINGERPRINT_MAX_LEN = 64

    async def dispatch(self, request: Request, call_next):
        fingerprint = request.headers.get("fingerprint", None)

        if fingerprint:
            fingerprint = fingerprint.strip()
            if (
                len(fingerprint) < self.FINGERPRINT_MIN_LEN
                or len(fingerprint) > self.FINGERPRINT_MAX_LEN
                or not fingerprint.isalnum()
            ):
                fingerprint = None

        request.state.fingerprint = fingerprint
        return await call_next(request)
