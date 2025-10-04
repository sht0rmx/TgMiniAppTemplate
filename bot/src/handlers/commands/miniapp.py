from aiogram import types
from aiogram.types import InlineKeyboardButton
from decouple import config

from utils import get_data


async def send_app(msg: types.Message):
    text, _, parse_mode = await get_data(msg, "app")
    markup = types.InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🚀 Miniapp", url=config("TG_STARTAPP_URL"))]])
    await msg.answer(text.format(user=msg.from_user.full_name), reply_markup=markup, parse_mode=parse_mode)