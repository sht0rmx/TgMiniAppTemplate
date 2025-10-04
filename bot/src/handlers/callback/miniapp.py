from aiogram import types
from handlers.commands.miniapp import send_app


async def callback_webapp(query: types.CallbackQuery):
    cmd = query.data.split(":", 1)[1]

    if cmd == "start":
        await send_app(query.message)

    await query.answer()