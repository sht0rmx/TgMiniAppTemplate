from aiogram import Router

inline_router = Router()

# Register inline handlers
import handlers.inline.base  # noqa: F401, E402