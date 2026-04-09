import os
import httpx
import logging
from typing import Optional

logger = logging.getLogger("uvicorn.error")


class YandexOAuthService:
    """Service for handling Yandex OAuth authentication flow."""
    
    YANDEX_AUTH_URL = "https://oauth.yandex.ru/authorize"
    YANDEX_TOKEN_URL = "https://oauth.yandex.ru/token"
    YANDEX_USER_INFO_URL = "https://login.yandex.ru/info"
    
    def __init__(self):
        self.client_id = os.getenv("YANDEX_CLIENT_ID")
        self.client_secret = os.getenv("YANDEX_CLIENT_SECRET")
        self.redirect_uri = os.getenv("YANDEX_REDIRECT_URI")
        
        if not all([self.client_id, self.client_secret, self.redirect_uri]):
            raise ValueError("Missing required Yandex OAuth environment variables")
    
    async def exchange_code_for_token(self, code: str) -> Optional[dict]:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from Yandex OAuth redirect
            
        Returns:
            Dictionary with access token and token info, or None on error
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.YANDEX_TOKEN_URL,
                    data={
                        "grant_type": "authorization_code",
                        "code": code,
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                    },
                    timeout=10.0,
                )
                
                if response.status_code != 200:
                    logger.error(f"Yandex token exchange failed: {response.text}")
                    return None
                
                return response.json()
        except Exception as e:
            logger.error(f"Error exchanging Yandex code: {e}")
            return None
    
    async def get_user_info(self, access_token: str) -> Optional[dict]:
        """
        Get user information from Yandex API.
        
        Args:
            access_token: Yandex OAuth access token
            
        Returns:
            Dictionary with user info, or None on error
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.YANDEX_USER_INFO_URL,
                    headers={
                        "Authorization": f"OAuth {access_token}",
                    },
                    timeout=10.0,
                )
                
                if response.status_code != 200:
                    logger.error(f"Failed to get Yandex user info: {response.text}")
                    return None
                
                return response.json()
        except Exception as e:
            logger.error(f"Error getting Yandex user info: {e}")
            return None
    
    async def authenticate_user(self, code: str) -> Optional[dict]:
        """
        Complete OAuth flow: exchange code for token and get user info.
        
        Args:
            code: Authorization code from Yandex OAuth redirect
            
        Returns:
            Dictionary with user info and access token, or None on error
        """
        # Exchange code for access token
        token_data = await self.exchange_code_for_token(code)
        if not token_data or "access_token" not in token_data:
            logger.error("Failed to get access token from Yandex")
            return None
        
        access_token = token_data.get("access_token")
        
        # Get user information
        user_info = await self.get_user_info(access_token)
        if not user_info:
            logger.error("Failed to get user info from Yandex")
            return None
        
        return {
            "user_info": user_info,
            "access_token": access_token,
            "token_data": token_data,
        }
