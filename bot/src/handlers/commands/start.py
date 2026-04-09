from aiogram import types
from aiogram.filters import Command

from handlers.commands import command_router
from utils.messages import get_data


@command_router.message(Command("start"))
async def send_start(msg: types.Message):
    args = await get_data(msg, "start")
    args["text"]=args["text"].format(user=msg.from_user.username)
    await msg.answer(**args)