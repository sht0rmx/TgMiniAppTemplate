from aiogram import Router

command_router = Router()

# Register command handlers
import handlers.commands.start  # noqa: F401, E402
import handlers.commands.help  # noqa: F401, E402
import handlers.commands.miniapp  # noqa: F401, E402
