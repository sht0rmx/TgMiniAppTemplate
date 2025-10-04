import asyncio

from handlers.commands import command_router
from handlers.callback import callback_router
from handlers.webapp import webapp_router
from handlers.inline import inline_router
from utils import dp, bot, logger, bot_info


async def main():
    dp.include_router(command_router)
    dp.include_router(callback_router)
    dp.include_router(inline_router)
    dp.include_router(webapp_router)
    await bot_info()
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning("Bot stopped manually")
