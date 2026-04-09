from handlers.inline import inline_router
from aiogram import types


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