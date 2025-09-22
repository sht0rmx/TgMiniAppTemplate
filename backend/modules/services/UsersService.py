import hashlib
import hmac
import urllib.parse
import json
import jwt
from datetime import datetime, timedelta, timezone

from decouple import config
from urllib.parse import unquote_plus
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from modules.db.models.RefreshToken import RefreshToken
from modules.services.TokenService import TokenService
from modules.db.models.User import User


class UsersService:
    def __init__(self):
        pass

    async def get_by_telegram_id(
        self, db: AsyncSession, telegram_id: int
    ) -> User | None:
        query = await db.execute(select(User).where(User.telegram_id == telegram_id))
        return query.scalar()

    async def curid_user(
        self,
        db: AsyncSession,
        telegram_id: int,
        username: str,
        firstname: str,
        photo: str | None,
        device_id: str,
        ip_address: str,
    ) -> dict:
        user_rec = await self.get_by_telegram_id(db, telegram_id=telegram_id)

        if not user_rec:
            user_rec = User(
                telegram_id=telegram_id,
                name=firstname,
                username=username,
                avatar_url=photo,
            )
            db.add(user_rec)
        else:
            user_rec.username = username
            user_rec.name = firstname
            user_rec.avatar_url = photo

        await db.commit()
        await db.refresh(user_rec)

        tokens = TokenService.create_tokens(user_rec.telegram_id)

        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        refresh_rec = RefreshToken(
            user_id=user_rec.id,
            device_id=device_id,
            ip_address=ip_address,
            token=tokens["refresh_token"],
            expires_at=expires_at
        )
        db.add(refresh_rec)
        await db.commit()
        await db.refresh(refresh_rec)

        return {
            "user": user_rec,
            "tokens": tokens
        }

    

    @staticmethod
    def _gen_token(user_id: int) -> str:
        payload = {
            "sub": str(user_id),
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(days=7),
        }
        return jwt.encode(
            payload,
            config("JWT_SECRET"),
            algorithm=str(config("JWT_ALG", default="HS256")),
        )


    @staticmethod
    def check_telegram_auth(hash_str, init_data, token, c_str="WebAppData") -> bool:
        """
        Validates the data received from the Telegram web app, using the
        method documented here:
        https://core.telegram.org/bots/webapps#validating-data-received-via-the-web-app
        """

        init_data = sorted(
            [
                chunk.split("=")
                for chunk in unquote_plus(init_data).split("&")
                if chunk[: len("hash=")] != "hash="
            ],
            key=lambda x: x[0],
        )
        init_data = "\n".join([f"{rec[0]}={rec[1]}" for rec in init_data])

        secret_key = hmac.new(c_str.encode(), token.encode(), hashlib.sha256).digest()
        data_check = hmac.new(secret_key, init_data.encode(), hashlib.sha256)

        return data_check.hexdigest() == hash_str

    @staticmethod
    def check_admin_token(token: str) -> bool:
        return token == config("API_TOKEN")
    
    @staticmethod
    def parse_init_data(init_data: str) -> dict:
        params = dict(x.split("=", 1) for x in init_data.split("&") if "=" in x)

        if "user" in params:
            raw_user = urllib.parse.unquote(params["user"])
            params["user"] = json.loads(raw_user)

        return params
