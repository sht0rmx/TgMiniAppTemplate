import asyncio
from typing import Any

from aiogram import types

from locales import translations
from utils import bot
from utils.logging import logger


async def get_data(
    message: types.Message,
    msg_id: str,
) -> dict[str, Any]:
    try:
        data = await translations.t(message, msg_id)
        if not data:
            return {"text": f"Message not found: {msg_id}"}

        text = "".join(data.get("msg", []))
        markup = None

        if "key" in data and data["key"]:
            key_buttons = []
            for row in data["key"].values():
                row_buttons = [types.KeyboardButton(text=btn) for btn in row]
                if row_buttons:
                    key_buttons.append(row_buttons)

            markup = types.ReplyKeyboardMarkup(
                keyboard=key_buttons, one_time_keyboard=True
            )

        elif "inline" in data and data["inline"]:
            inline_buttons = []
            for row in data["inline"].values():
                row_buttons = [
                    (
                        types.InlineKeyboardButton(
                            text=btn_text, url=callback.replace("link::", "", 1)
                        )
                        if isinstance(callback, str) and callback.startswith("link::")
                        else types.InlineKeyboardButton(
                            text=btn_text, callback_data=callback
                        )
                    )
                    for btn_text, callback in row.items()
                ]

                if row_buttons:
                    inline_buttons.append(row_buttons)

            markup = types.InlineKeyboardMarkup(inline_keyboard=inline_buttons)

        parse_mode = data.get("parse_mode", None)
        return {"text": text, "reply_markup": markup, "parse_mode": parse_mode}

    except Exception as e:
        logger.error(f"Error in get_data: {e}")
        return {"text": f"Error: {e}"}


async def ask(message: types.Message) -> bool:
    try:
        answers = await translations.t(message, msg_id="answers")
        logger.debug(f"no_val: {answers}")
        return message.text.lower() == answers["yes"]
    except Exception as e:
        logger.error(f"Error in ask: {e}")
        return False


async def next_step(message: types.Message) -> bool:
    try:
        cancel_val = await translations.t(message, msg_id="cancel")
        logger.debug(cancel_val)
        return message.text.lower() not in cancel_val
    except Exception as e:
        logger.error(f"Error in next_step: {e}")
        return False


async def auto_delete(message: types.Message, delay: int = 2) -> None:
    try:
        await asyncio.sleep(delay)
        await bot.delete_message(message.chat.id, message.message_id)
    except Exception as e:
        logger.error(f"Error in auto_delete: {e}")
