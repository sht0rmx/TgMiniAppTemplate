import os

import jwt
from fastapi import Depends, HTTPException, Request, WebSocket
from starlette.middleware.base import BaseHTTPMiddleware

from app.database.database import Banned, Expired, NotFound, Revoked, db_client


async def require_auth(request: Request):
    auth = request.headers.get("authorization")
    if not auth:
        raise HTTPException(401, "Missing Authorization header")
    if not auth.startswith("Bearer "):
        raise HTTPException(401, "Unsupported auth header")

    token = auth.split(" ")[1]
    try:
        payload = jwt.decode(
            token,
            os.getenv("JWT_SECRET"),
            algorithms=[os.getenv("JWT_ALG", "HS256")]
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid token")

    if payload.get("is_bot"):
        try:
            await db_client.get_api_key(api_key_id=payload.get("sid"))
        except (NotFound, Banned):
            raise HTTPException(401, "Invalid Api key metadata")
    else:
        try:
            await db_client.get_refresh_session(
                fingerprint=request.state.fingerprint,
                session_id=payload.get("sid")
                )
        except (NotFound, Expired, Revoked):
            raise HTTPException(401, "Invalid Refresh session metadata")

    request.state.user_id = payload.get("sub")
    request.state.role = payload.get("role")
    request.state.session_id = payload.get("sid")

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
