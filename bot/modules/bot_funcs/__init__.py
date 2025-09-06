import time
from typing import Optional, Union, Tuple
from telebot import types

from modules import bot
from modules.plugins import translations
from modules.db import dbclient
from modules.logging import logger

def get_data(
    message: types.Message,
    msg_id: str,
    only_txt: bool = False
) -> Union[Tuple[str, Optional[Union[types.ReplyKeyboardMarkup, types.InlineKeyboardMarkup]]], str]:
    try:
        data = translations.t(message.from_user.id, msg_id)
        if not data:
            return f"Message not found: {msg_id}", None

        text = "".join(data["msg"])

        if "key" in data:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            for row in data["key"].values():
                buttons = [types.KeyboardButton(text=btn) for btn in row]
                markup.add(*buttons)
        elif "inline" in data:
            markup = types.InlineKeyboardMarkup()
            for row in data["inline"].values():
                buttons = [
                    types.InlineKeyboardButton(text=btn_text, callback_data=callback)
                    for btn_text, callback in row.items()
                ]
                markup.add(*buttons)
        else:
            markup = None

        return (text, markup) if not only_txt else text
    except Exception as e:
        logger.error(f"Error in get_data: {e}")
        return f"Error: {e}", None


def next_step(message: types.Message) -> bool:
    try:
        if message.text in translations.t(message.from_user.id, "answers/yes"):
            hint_id = bot.send_message(message.chat.id, "^_^")
            time.sleep(1)
            bot.delete_message(message.chat.id, hint_id.message_id)
            return True
        return False
    except Exception as e:
        logger.error(f"Error in next_step: {e}")
        return False

def ask(message: types.Message) -> bool:
    try:
        lang = dbclient.what_lang(message.from_user.id)
        if message.text.lower() == translations.t(lang, "answers/yes"):
            return False
        hint_id = bot.send_message(message.chat.id, ":|")
        auto_delete(hint_id, 1)
        return True
    except Exception as e:
        logger.error(f"Error in ask: {e}")
        return True

def auto_delete(message: types.Message, delay: int = 0) -> None:
    try:
        time.sleep(delay)
        bot.delete_message(message.chat.id, message.message_id)
    except Exception as e:
        logger.error(f"Error in auto_delete: {e}")

def bot_info() -> None:
    try:
        me = bot.get_me()
        logger.debug(f"bot '{me.full_name}' will started")
        logger.debug(f"username: @{me.username}")
        logger.debug(f"bot id: {me.id}")
    except Exception as e:
        logger.error(f"Error in bot_info: {e}")
