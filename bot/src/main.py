import asyncio

from handlers.callback import callback_router
from handlers.commands import command_router
from handlers.inline import inline_router
from handlers.webapp import webapp_router
from api import api_client
from utils import bot, bot_info, dp, logger


async def main():
    dp.include_router(command_router)
    dp.include_router(callback_router)
    dp.include_router(inline_router)
    dp.include_router(webapp_router)

    await bot_info()
    await api_client.init()

    try:
        await dp.start_polling(bot)
    finally:
        await api_client.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning("Bot stopped manually")
