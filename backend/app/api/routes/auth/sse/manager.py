import asyncio
import json
import os
from datetime import datetime

from app.utils import parse_expire

LOGIN_EXPIRE_SEC = parse_expire(os.getenv("LOGIN_EXPIRE", "5m"))

class SSEManager:
    def __init__(self):
        self.queues: dict[str, asyncio.Queue] = {}
        self.start_times: dict[str, datetime] = {}

    def get_queue(self, login_id: str) -> asyncio.Queue:
        if login_id not in self.queues:
            self.queues[login_id] = asyncio.Queue()
            self.start_times[login_id] = datetime.now()
        return self.queues[login_id]

    async def push_event(self, login_id: str, data: dict):
        queue = self.get_queue(login_id)
        await queue.put(data)

    async def event_generator(self, login_id: str):
        queue = self.get_queue(login_id)
        start_time = self.start_times[login_id]

        try:
            yield f"data: {json.dumps({'type': 'connected'})}\n\n"

            while True:
                elapsed = datetime.now() - start_time
                if elapsed > LOGIN_EXPIRE_SEC:
                    break

                try:
                    event = await asyncio.wait_for(queue.get(), timeout=20)
                    print(f"[SSE] sending {event}")
                    yield f"data: {json.dumps(event)}\n\n"
                except asyncio.TimeoutError:
                    yield ": keep-alive\n\n"

        finally:
            self.queues.pop(login_id, None)
            self.start_times.pop(login_id, None)

sse_manager = SSEManager()
