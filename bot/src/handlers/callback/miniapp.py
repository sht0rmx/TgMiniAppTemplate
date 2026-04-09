from aiogram import types
from handlers.commands.miniapp import send_app
from handlers.callback import callback_router


@callback_router.callback_query(lambda q: q.data and q.data.startswith("webapp:"))
async def callback_webapp(query: types.CallbackQuery):
    cmd = query.data.split(":", 1)[1]

    if cmd == "start":
        await send_app(query.message)

    await query.answer()