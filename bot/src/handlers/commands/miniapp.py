from aiogram.types import InlineKeyboardButton
from aiogram import types
from decouple import config
from aiogram.filters import Command

from handlers.commands import command_router
from utils.messages import get_data


@command_router.message(Command("app"))
async def send_app(msg: types.Message):
    args = await get_data(msg, "start")
    args["text"] = args["text"].format(user=msg.from_user.username)
    args["reply_markup"] = types.InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🚀 Miniapp", url=config("TG_STARTAPP_URL"))]])
    await msg.answer(**args)