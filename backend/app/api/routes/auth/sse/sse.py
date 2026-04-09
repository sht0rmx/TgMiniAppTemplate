import asyncio

from fastapi import APIRouter
from fastapi.responses import JSONResponse, StreamingResponse

from app.api.routes.auth.sse.manager import sse_manager
from app.database.database import Expired, NotFound, db_client
from app.utils import create_hash

router = APIRouter(prefix="/sse", tags=["sse"])


@router.get("/check/{login_id}")
async def sse_endpoint(login_id: str):
    login_hash = create_hash("LOGIN_SECRET", str(login_id))
    try:
        await db_client.get_login_session(login_hash=str(login_hash))
    except (NotFound, Expired):
        print("error")
        return JSONResponse({"detail": "login_id not found"}, status_code=400)

    async def event_stream():
        try:
            async for event in sse_manager.event_generator(login_id):
                yield event
        except asyncio.CancelledError:
            print(f"Client disconnected: {login_id}")

    return StreamingResponse(event_stream(), media_type="text/event-stream")
