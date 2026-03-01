from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from app.database.database import NotFound, db_client
from app.middleware.auth import require_auth
from app.services.caching import cache

router = APIRouter(tags=["check"])

@cache
@router.get("/check", dependencies=[Depends(require_auth)])
async def check(request: Request):
    try:
        user = await db_client.get_user(uid=request.state.user_id)

        user_entity = {
            "id": str(user.id),
            "telegram_id": user.telegram_id,
            "username": user.username,
            "name": user.name,
            "role": user.role,
            "avatar_url": user.avatar_url,
            "last_seen": user.last_seen.isoformat(),
            "created_at": user.created_at.isoformat()
        }
        return JSONResponse(content={"user": user_entity}, status_code=200)
    except NotFound:
        return JSONResponse({"detail": "user not found"}, status_code=406)

