from aiogram import Router, types

from handlers.callback.commands import callback_command
from handlers.callback.miniapp import callback_webapp

callback_router = Router()


@callback_router.callback_query(lambda q: q.data and q.data.startswith("command:"))
async def handle_command(query: types.CallbackQuery):
    await callback_command(query)

@callback_router.callback_query(lambda q: q.data and q.data.startswith("webapp:"))
async def handle_command(query: types.CallbackQuery):
    await callback_webapp(query)
