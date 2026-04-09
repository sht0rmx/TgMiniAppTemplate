import os

from redis.asyncio import Redis


class RedisClient:
    def __init__(self):
        self.client: Redis = Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            password=os.getenv("REDIS_PASSWORD"),
            decode_responses=True
        )

    async def init(self):
        print("[REDIS] init")
        await self.client.ping()

    async def close(self):
        if self.client:
            await self.client.close()

    async def get(self, key: str):
        return await self.client.get(key)

    async def set_(self, key: str, value: str | int, ex: int | None = None):
        return await self.client.set(key, str(value), ex=ex)

    async def delete(self, key: str):
        return await self.client.delete(key)

    async def incr(self, key: str):
        return await self.client.incr(key)


redis_client = RedisClient()
