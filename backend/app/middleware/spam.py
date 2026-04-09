from functools import wraps
from typing import Callable

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.database.redis import redis_client


def rate_limit(limit: int, period: int = 60):
    """
    Decorator to set per-endpoint rate limits.
    
    Args:
        limit: Number of requests allowed
        period: Time period in seconds
    
    Example:
        @rate_limit(limit=3, period=300)
        async def transfer_user(...):
            ...
    """
    def decorator(func: Callable) -> Callable:
        func._rate_limit = (limit, period)
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        wrapper._rate_limit = (limit, period)
        return wrapper
    return decorator


class RateLimitMiddleware:
    def __init__(self, app: FastAPI, limit: int = 5, period: int = 10):
        self.app = app
        self.limit = limit  # Default global limit
        self.period = period  # Default global period

    async def __call__(self, request: Request, call_next):
        if request.method == "OPTIONS":
            return await call_next(request)

        ip = request.client.host if request.client else ""
        path = request.url.path

        # Find the matching route in the app
        ep_limit = self.limit
        ep_period = self.period
        
        for route in self.app.routes:
            if hasattr(route, "path") and path.startswith(route.path):
                if hasattr(route, "endpoint") and hasattr(route.endpoint, "_rate_limit"):
                    ep_limit, ep_period = route.endpoint._rate_limit
                break

        # Apply endpoint-specific rate limit
        ep_key = f"rate:{ip}:{path}"
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

        # Apply global rate limit
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
