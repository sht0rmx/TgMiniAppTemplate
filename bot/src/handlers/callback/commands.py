from aiogram import types

from handlers import send_start, send_help


async def callback_command(query: types.CallbackQuery):
    cmd = query.data.split(":", 1)[1]

    if cmd == "start":
        await send_start(query.message)
    elif cmd == "help":
        await send_help(query.message)

    await query.answer()