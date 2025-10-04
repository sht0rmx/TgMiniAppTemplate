from aiogram import types

from handlers import webapp_handle
from utils import get_data


@webapp_handle(lambda handler, code, data: handler == "hello")
async def hello_msg(msg: types.Message, code, data):
    text, markup, parse_mode = await get_data(msg, code)
    await msg.answer(
        text.format(id=data.get('id')),
        reply_markup=markup,
        parse_mode=parse_mode
    )
