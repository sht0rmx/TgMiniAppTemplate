import logging

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from app.database.database import NotFound, db_client
from app.middleware.auth import deny_bot, require_auth, require_origin
from app.schemas.models import SendMessageRequest
from app.services.telegram import telegram_service

router = APIRouter(prefix="/bot", tags=["bot"])

@router.post(
    "/send",
    dependencies=[Depends(require_origin), Depends(deny_bot()), Depends(require_auth)],
)
async def send_message_to_user(request: Request, body: SendMessageRequest):
    user_id = request.state.user_id
    if not user_id:
        return JSONResponse({"detail": "Missing user_id"}, status_code=400)

    text = body.text.strip()
    if not text:
        return JSONResponse({"detail": "Message text is empty"}, status_code=400)

    if len(text) > 4096:
        return JSONResponse(
            {"detail": "Message too long. Max 4096 characters"}, status_code=400
        )

    try:
        user = await db_client.get_user(uid=user_id)
    except NotFound:
        return JSONResponse({"detail": "User not found"}, status_code=404)

    sent = await telegram_service.send_message(
        chat_id=user.telegram_id,
        text=text,
        parse_mode="HTML",
    )

    if sent:
        return JSONResponse({"detail": "Message sent"}, status_code=200)

    return JSONResponse(
        {"detail": "Failed to send message. Make sure you started the bot."},
        status_code=400,
    )
