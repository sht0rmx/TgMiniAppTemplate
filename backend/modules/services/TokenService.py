from datetime import datetime, timedelta, timezone
import jwt
from decouple import config


class TokenService:
    JWT_SECRET: str = str(config("JWT_SECRET"))
    JWT_ALG: str = str(config("JWT_ALG", default="HS256"))

    @staticmethod
    def create_access_token(user_id: str | int, minutes: int = 15) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "sub": str(user_id),
            "type": "access",
            "iat": now,
            "exp": now + timedelta(minutes=minutes),
        }
        return jwt.encode(payload, TokenService.JWT_SECRET, algorithm=TokenService.JWT_ALG)

    @staticmethod
    def create_refresh_token(user_id: str | int, days: int = 7) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "sub": str(user_id),
            "type": "refresh",
            "iat": now,
            "exp": now + timedelta(days=days),
        }
        return jwt.encode(payload, TokenService.JWT_SECRET, algorithm=TokenService.JWT_ALG)

    @classmethod
    def create_tokens(cls, user_id: str | int) -> dict:
        return {
            "access_token": cls.create_access_token(user_id),
            "refresh_token": cls.create_refresh_token(user_id),
        }
