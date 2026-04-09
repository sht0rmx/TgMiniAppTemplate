from aiogram import Router

callback_router = Router()

# Register callback handlers
import handlers.callback.commands  # noqa: F401, E402
import handlers.callback.miniapp  # noqa: F401, E402
