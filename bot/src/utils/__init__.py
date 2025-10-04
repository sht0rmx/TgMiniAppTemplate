import asyncio
from typing import Union, Tuple

import os
from aiogram import Bot, Dispatcher, types
from dotenv import load_dotenv

from utils.logging import logger
from locales import translations

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found in environment")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


async def get_data(
    message: types.Message,
    msg_id: str,
) -> Tuple[str, Union[types.ReplyKeyboardMarkup, types.InlineKeyboardMarkup, None], Union[str, None]]:
    """
    Возвращает (text, markup, parse_mode) для указанного msg_id
    """
    try:
        data = translations.t(message, msg_id)
        if not data:
            return f"Message not found: {msg_id}", None, None

        text = "".join(data.get("msg", []))
        markup = None

        if "key" in data and data["key"]:
            key_buttons = []
            for row in data["key"].values():
                row_buttons = [types.KeyboardButton(text=btn) for btn in row]
                if row_buttons:
                    key_buttons.append(row_buttons)

            markup = types.ReplyKeyboardMarkup(keyboard=key_buttons, one_time_keyboard=True)

        elif "inline" in data and data["inline"]:
            inline_buttons = []
            for row in data["inline"].values():
                row_buttons = [
                    types.InlineKeyboardButton(text=btn_text, callback_data=callback)
                    for btn_text, callback in row.items()
                ]
                if row_buttons:
                    inline_buttons.append(row_buttons)

            markup = types.InlineKeyboardMarkup(inline_keyboard=inline_buttons)

        parse_mode = data.get("parse_mode", None)
        return text, markup, parse_mode

    except Exception as e:
        logger.error(f"Error in get_data: {e}")
        return f"Error: {e}", None, None


async def ask(message: types.Message) -> bool:
    try:
        no_val = translations.t(message, "answers").get("no", "no").lower()
        return message.text.lower() != no_val
    except Exception as e:
        logger.error(f"Error in ask: {e}")
        return False


async def next_step(message: types.Message) -> bool:
    try:
        return await ask(message)
    except Exception as e:
        logger.error(f"Error in next_step: {e}")
        return False


async def auto_delete(message: types.Message, delay: int = 0) -> None:
    try:
        await asyncio.sleep(delay)
        await bot.delete_message(message.chat.id, message.message_id)
    except Exception as e:
        logger.error(f"Error in auto_delete: {e}")


async def bot_info() -> None:
    try:
        me = await bot.get_me()
        logger.debug(f"Bot '{me.full_name}' started")
        logger.debug(f"Username: @{me.username}")
        logger.debug(f"Bot ID: {me.id}")
    except Exception as e:
        logger.error(f"Error in bot_info: {e}")
