from aiogram import types
from utils import get_data


async def send_start(msg: types.Message):
    text, markup, parse_mode = await get_data(msg, "start")
    await msg.answer(text.format(user=msg.from_user.username), reply_markup=markup, parse_mode=parse_mode)