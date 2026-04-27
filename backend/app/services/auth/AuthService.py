import hmac
import os
import uuid
from datetime import datetime
from urllib.parse import unquote

import jwt
from fastapi.responses import JSONResponse

from app.api.routes.auth.sse.manager import sse_manager
from app.database.database import Database, NotFound, db_client
from app.utils import create_hash, parse_expire


class AuthUtils:
    @staticmethod
    def gen_jwt_token(
        user_id, session_id, role: str = "user", is_bot: bool = False
    ) -> str:
        delta = parse_expire(os.getenv("ACCESS_EXPITRE", "30m"))
        payload = {
            "sub": str(user_id),
            "sid": str(session_id),
            "role": str(role),
            "is_bot": bool(is_bot),
            "exp": datetime.now() + delta,
        }
        return jwt.encode(
            payload,
            os.getenv("JWT_SECRET"),
            algorithm=os.getenv("JWT_ALG", "HS256"),
        )

    @staticmethod
    def check_initdata(initdata: str, hash_str: str) -> bool:
        token = os.getenv("BOT_TOKEN")
        if not token:
            return False

        idl = sorted(
            [
                chunk.split("=", 1)
                for chunk in unquote(initdata).split("&")
                if not chunk.startswith("hash=")
            ],
            key=lambda x: x[0],
        )
        dcs = "\n".join([f"{k}={v}" for k, v in idl])

        secret_key = create_hash(key="WebAppData", msg=token, from_env=False, hex=False)
        created_hash = create_hash(key=secret_key, msg=dcs, from_env=False, hex=True)

        if isinstance(created_hash, str):
            return hmac.compare_digest(created_hash, hash_str)

        return False


class AuthService:
    def __init__(self, db: Database | None = None):
        self._db = db or db_client

    def json_with_refresh_cookie(
        self,
        *,
        access_token: str,
        refresh_token: str,
        recovery_code: str | None = None,
        cookie_samesite: str = "lax",
        cookie_path: str | None = None,
    ) -> JSONResponse:
        resp = JSONResponse(
            content={"access_token": access_token, "recovery_code": recovery_code},
            status_code=200,
        )
        cookie_kwargs: dict = {
            "key": "refresh_token",
            "value": str(refresh_token),
            "httponly": True,
            "max_age": int(
                parse_expire(os.getenv("REFRESH_EXPIRE", "60d")).total_seconds()
            ),
            "secure": not bool(os.getenv("DEV", "")),
            "samesite": cookie_samesite,
        }
        if cookie_path is not None:
            cookie_kwargs["path"] = cookie_path
        resp.set_cookie(**cookie_kwargs)
        return resp

    async def accept_login(
        self,
        user_id: str,
        role: str,
        *,
        code: str = "",
        login: str = "",
    ) -> None:
        if login:
            login_hash = create_hash("LOGIN_SECRET", login)
            login_session = await self._db.get_login_session(login_hash=login_hash)
        elif code:
            login_session = await self._db.get_login_session(code=code)
        else:
            raise NotFound("Login session not found")

        login_session = await self._db.set_one_time_code_accepted(login_session.id)

        token = str(uuid.uuid4())
        session = await self._db.create_refresh_session(
            refresh_token=token,
            fingerprint=str(login_session.fingerprint),
            ip=str(login_session.ip),
            user_id=user_id,
        )
        access_token = AuthUtils.gen_jwt_token(
            user_id=user_id, session_id=session.id, role=role
        )
        await sse_manager.push_event(
            login_id=str(login_session.sse_login_id),
            data={"type": "auth_success", "access_token": access_token},
        )


auth_service = AuthService()
