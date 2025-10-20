from aiogram import types

from utils import get_data


async def send_help(msg: types.Message):
    text, markup, parse_mode = await get_data(msg, "help")
    await msg.answer(text, reply_markup=markup, parse_mode=parse_mode)