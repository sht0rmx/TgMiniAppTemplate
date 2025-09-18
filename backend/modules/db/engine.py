import asyncio
from decouple import config

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlmodel.ext.asyncio.session import AsyncSession


engine = create_async_engine(str(config("BD_URL")), echo=True)
async_session = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)
Base = declarative_base()


class Database:
    def __init__(self):
        self.engine = engine
        self.async_session = async_sessionmaker(
            self.engine,
            expire_on_commit=False,
            class_=AsyncSession,
        )

    async def create_db(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def close(self):
        await self.engine.dispose()

    async def get_session(self) -> AsyncSession:
        async with async_session() as session:
            yield session
