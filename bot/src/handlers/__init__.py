from aiogram import Router, types
from aiogram.filters import Command

from handlers.commands.start import send_start
from handlers.commands.help import send_help

router = Router()


@router.message(Command("start"))
async def start_command(msg: types.Message):
    await send_start(msg)


@router.message(Command("help"))
async def help_command(msg: types.Message):
    await send_help(msg)