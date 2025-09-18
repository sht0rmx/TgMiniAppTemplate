import asyncio

from modules.logging import logger


async def init_db():
    db = database.Database()
    await db.create_db()
    await db.close()


async def main():
    await init_db()
    dp.include_router(router)
    await start_worker(bot)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(" ")