import os

import httpx
from dotenv import load_dotenv

from utils.logging import logger

load_dotenv()

API_ENDPOINT = os.getenv("API_ENDPOINT", "").rstrip("/")
API_KEY = os.getenv("API_KEY", "")


class ApiClient:
    """HTTP client for backend API with automatic JWT auth via API key."""

    def __init__(self):
        self.base_url = API_ENDPOINT
        self.api_key = API_KEY
        self.access_token: str | None = None
        self._client: httpx.AsyncClient | None = None

    async def init(self):
        """Initialize HTTP client and authenticate with the backend."""
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(30.0),
        )

        if self.api_key:
            await self._authenticate()
        else:
            logger.warning("[API] API_KEY not set — skipping backend auth")

    async def _authenticate(self):
        """Authenticate with the backend using the API key to get a JWT."""
        try:
            resp = await self._client.get(
                "/api/v1/auth/login/api-key",
                headers={"Authorization": f"Bearer {self.api_key}"},
            )

            if resp.status_code == 200:
                data = resp.json()
                self.access_token = data.get("access_token")
                user = data.get("user", {})
                logger.info(
                    f"[API] Authenticated as {user.get('username', 'unknown')} "
                    f"(role: {user.get('role', '?')})"
                )
            else:
                logger.error(f"[API] Auth failed ({resp.status_code}): {resp.text}")
        except httpx.ConnectError:
            logger.error(f"[API] Cannot connect to backend at {self.base_url}")
        except Exception as e:
            logger.error(f"[API] Auth error: {e}")

    async def _get_headers(self) -> dict[str, str]:
        """Return auth headers with current JWT token."""
        if not self.access_token:
            return {}
        return {"Authorization": f"Bearer {self.access_token}"}

    async def request(
        self,
        method: str,
        path: str,
        **kwargs,
    ) -> httpx.Response | None:
        """Make an authenticated request to the backend API."""
        if not self._client:
            logger.error("[API] Client not initialized — call init() first")
            return None

        headers = await self._get_headers()
        headers.update(kwargs.pop("headers", {}))

        try:
            resp = await self._client.request(
                method, path, headers=headers, **kwargs
            )

            # Re-auth on 401 and retry once
            if resp.status_code == 401 and self.api_key:
                logger.warning("[API] Token expired, re-authenticating...")
                await self._authenticate()
                headers = await self._get_headers()
                resp = await self._client.request(
                    method, path, headers=headers, **kwargs
                )

            return resp
        except Exception as e:
            logger.error(f"[API] Request error ({method} {path}): {e}")
            return None

    async def get(self, path: str, **kwargs) -> httpx.Response | None:
        return await self.request("GET", path, **kwargs)

    async def post(self, path: str, **kwargs) -> httpx.Response | None:
        return await self.request("POST", path, **kwargs)

    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            logger.debug("[API] Client closed")


api_client = ApiClient()
