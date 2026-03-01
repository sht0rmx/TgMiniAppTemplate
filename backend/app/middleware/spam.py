from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.database.redis import redis_client


# Per-endpoint rate limit rules: path prefix -> (limit, period_seconds)
AUTH_RATE_LIMITS: dict[str, tuple[int, int]] = {
    "/api/v1/auth/login/": (5, 60),       # 5 login attempts per 60s
    "/api/v1/auth/token/get-tokens": (10, 60),  # 10 token refreshes per 60s
    "/api/v1/auth/token/recovery": (3, 300),    # 3 recovery attempts per 5min
    "/api/v1/auth/token/transfer": (3, 300),    # 3 transfer attempts per 5min
}


class RateLimitMiddleware:
    def __init__(self, app: FastAPI, limit: int = 5, period: int = 10):
        self.app = app
        self.limit = limit
        self.period = period

    async def __call__(self, request: Request, call_next):
        if request.method == "OPTIONS":
            return await call_next(request)

        ip = request.client.host if request.client else ""

        path = request.url.path
        for prefix, (ep_limit, ep_period) in AUTH_RATE_LIMITS.items():
            if path.startswith(prefix):
                ep_key = f"rate:{ip}:{prefix}"
                ep_count = await redis_client.get(ep_key)

                if ep_count is None:
                    await redis_client.set_(ep_key, 1, ex=ep_period)
                elif int(ep_count) < ep_limit:
                    await redis_client.incr(ep_key)
                else:
                    return JSONResponse(
                        status_code=429,
                        content={"detail": "Too Many Requests"}
                    )
                break

        key = f"rate:{ip}"
        count = await redis_client.get(key)

        if count is None:
            await redis_client.set_(key, 1, ex=self.period)
        elif int(count) < self.limit:
            await redis_client.incr(key)
        else:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too Many Requests"}
            )

        response = await call_next(request)
        return response
