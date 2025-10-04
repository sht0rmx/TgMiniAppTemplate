from aiogram import Router, types
from aiogram.filters import Command

from handlers.commands.miniapp import send_app
from handlers.commands.start import send_start
from handlers.commands.help import send_help

command_router = Router()


@command_router.message(Command("start"))
async def start_command(msg: types.Message):
    await send_start(msg)


@command_router.message(Command("help"))
async def help_command(msg: types.Message):
    await send_help(msg)

@command_router.message(Command("app"))
async def app_command(msg: types.Message):
    await send_app(msg)
