import logging
import os
from typing import Any, Optional

import httpx

logger = logging.getLogger("uvicorn.error")


class YandexOAuthService:
    YANDEX_AUTH_URL = "https://oauth.yandex.ru/authorize"
    YANDEX_TOKEN_URL = "https://oauth.yandex.ru/token"
    YANDEX_USER_INFO_URL = "https://login.yandex.ru/info"

    def __init__(self) -> None:
        self.client_id = os.getenv("YANDEX_CLIENT_ID")
        self.client_secret = os.getenv("YANDEX_CLIENT_SECRET")
        self.redirect_uri = os.getenv("YANDEX_REDIRECT_URI")
        if not all([self.client_id, self.client_secret, self.redirect_uri]):
            raise ValueError("Missing required Yandex OAuth environment variables")

    async def exchange_code_for_token(self, code: str) -> Optional[dict]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.YANDEX_TOKEN_URL,
                    data={
                        "grant_type": "authorization_code",
                        "code": code,
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "redirect_uri": self.redirect_uri,
                    },
                    timeout=10.0,
                )
                if response.status_code != 200:
                    logger.error("Yandex token exchange failed: %s", response.text)
                    return None
                return response.json()
        except Exception as e:
            logger.error("Error exchanging Yandex code: %s", e)
            return None

    async def get_user_info(self, access_token: str) -> Optional[dict]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.YANDEX_USER_INFO_URL,
                    headers={"Authorization": f"OAuth {access_token}"},
                    timeout=10.0,
                )
                if response.status_code != 200:
                    logger.error("Failed to get Yandex user info: %s", response.text)
                    return None
                return response.json()
        except Exception as e:
            logger.error("Error getting Yandex user info: %s", e)
            return None

    async def authenticate_user(self, code: str) -> Optional[dict]:
        token_data = await self.exchange_code_for_token(code)
        if not token_data or "access_token" not in token_data:
            logger.error("Failed to get access token from Yandex")
            return None
        access_token = token_data.get("access_token")
        user_info = await self.get_user_info(access_token)
        if not user_info:
            logger.error("Failed to get user info from Yandex")
            return None
        return {
            "user_info": user_info,
            "access_token": access_token,
            "token_data": token_data,
        }

    @staticmethod
    def parse_profile(user_info: dict[str, Any]) -> dict[str, Any]:
        yandex_id = user_info.get("id")
        username = user_info.get("login", "")
        email = user_info.get("default_email", "")
        name = (
            f"{user_info.get('first_name', '')} {user_info.get('last_name', '')}"
        ).strip()
        avatar_url = user_info.get("default_avatar_id")
        if avatar_url:
            avatar_url = f"https://avatars.yandex.net/get-yapic/{avatar_url}/islands-200"
        if not name:
            name = username or email
        return {
            "yandex_id": str(yandex_id) if yandex_id is not None else None,
            "username": username,
            "email": email,
            "name": name,
            "avatar_url": avatar_url,
        }
