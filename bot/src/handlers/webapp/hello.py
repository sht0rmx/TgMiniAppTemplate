from aiogram import types

from handlers.webapp import webapp_handle
from utils.messages import get_data


@webapp_handle(lambda handler, code, data: handler == "hello")
async def hello_msg(msg: types.Message, code, data):
    args = await get_data(msg, code)
    args["text"] = args["text"].format(id=data.get('id'))
    await msg.answer(**args)
