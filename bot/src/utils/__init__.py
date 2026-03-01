import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from utils.logging import logger

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found in environment")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


async def bot_info() -> None:
    try:
        me = await bot.get_me()
        logger.debug(f"Bot '{me.full_name}' started")
        logger.debug(f"Username: @{me.username}")
        logger.debug(f"Bot ID: {me.id}")
    except Exception as e:
        logger.error(f"Error in bot_info: {e}")
