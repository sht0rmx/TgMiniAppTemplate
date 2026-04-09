import json
from collections.abc import Callable
from functools import wraps
from typing import Any

from app.database.redis import redis_client


def cache(ttl: int = 60):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            key = f"cache:{func.__name__}:{json.dumps([args, kwargs], default=str)}"
            cached = await redis_client.get(key)
            if cached is not None:
                return json.loads(cached)

            result = await func(*args, **kwargs)
            await redis_client.set_(key, json.dumps(result), ex=ttl)
            return result

        return wrapper
    return decorator
