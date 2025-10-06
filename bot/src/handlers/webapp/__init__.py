import json
from functools import wraps

from aiogram import Router, types

webapp_router = Router()


def webapp_handle(filter_func=None):
    def decorator(func):
        @webapp_router.message(lambda msg: msg.web_app_data is not None)
        @wraps(func)
        async def wrapper(msg: types.Message, *args, **kwargs):
            try:
                payload = json.loads(msg.web_app_data.data)
                handler = payload.get("handler")
                code = payload.get("code")
                data = payload.get("data", {})

                if filter_func and not filter_func(handler, code, data):
                    return

                await func(msg, code, data, *args, **kwargs)
            except Exception as e:
                await msg.answer(f"Error parsing MiniApp data: {e}")
        return wrapper
    return decorator