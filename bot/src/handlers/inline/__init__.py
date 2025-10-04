from aiogram import Router, types
from aiogram.filters import Command

from handlers.commands.start import send_start
from handlers.commands.help import send_help

inline_router = Router()


@inline_router.inline_query()
async def inline_any(query: types.InlineQuery):
    results = [
        types.InlineQueryResultArticle(
            id="1",
            title="Ask",
            input_message_content=types.InputTextMessageContent(
                message_text=f"You typed: {query.query or 'nothing'}"
            )
        )
    ]
    await query.answer(results=results, cache_time=0)