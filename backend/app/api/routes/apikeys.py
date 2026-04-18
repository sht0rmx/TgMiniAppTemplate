import secrets

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from app.database.database import Banned, NotFound, db_client
from app.middleware.auth import deny_bot, require_auth
from app.schemas.models import CreateApiKeyRequest

router = APIRouter(prefix="/apikeys", tags=["API Keys"])


@router.get(
    "/all",
    dependencies=[Depends(deny_bot)],
)
async def list_api_keys(request: Request):
    user_id = request.state.user_id
    if not user_id:
        return JSONResponse({"detail": "Missing user_id"}, status_code=400)

    try:
        keys = await db_client.get_api_keys_for_user(user_id=user_id)
    except NotFound:
        return JSONResponse({"keys": []}, status_code=200)

    result = []
    for k in keys:
        result.append(
            {
                "id": str(k.id),
                "name": k.name,
                "banned": bool(k.banned),
                "createdAt": k.created_at.isoformat(),
            }
        )

    return JSONResponse({"keys": result}, status_code=200)


@router.post(
    "/create",
    dependencies=[Depends(deny_bot)],
)
async def create_api_key(request: Request, body: CreateApiKeyRequest):
    user_id = request.state.user_id
    if not user_id:
        return JSONResponse({"detail": "Missing user_id"}, status_code=400)

    name = body.name.strip()
    if not name or len(name) > 30:
        return JSONResponse(
            {"detail": "Name must be 1-30 characters"}, status_code=400
        )

    raw_key = f"sk_{secrets.token_urlsafe(32)}"

    try:
        await db_client.create_api_key(
            user_id=user_id, name=name, api_key=raw_key
        )
    except ValueError as e:
        return JSONResponse({"detail": str(e)}, status_code=400)

    return JSONResponse(
        {"detail": "created", "key": raw_key, "name": name}, status_code=201
    )


@router.delete(
    "/{key_id}",
    dependencies=[Depends(deny_bot)],
)
async def delete_api_key(request: Request, key_id: str):
    user_id = request.state.user_id
    if not user_id:
        return JSONResponse({"detail": "Missing user_id"}, status_code=400)

    try:
        key = await db_client.get_api_key(api_key_id=key_id)
    except (NotFound, Banned):
        return JSONResponse({"detail": "API key not found"}, status_code=404)

    if str(key.user_id) != str(user_id):
        return JSONResponse({"detail": "Access denied"}, status_code=403)

    await db_client.delete_api_key(key_id=key_id)
    return JSONResponse({"detail": "deleted"}, status_code=200)


@router.patch(
    "/{key_id}/ban",
    dependencies=[Depends(deny_bot)],
)
async def toggle_ban_api_key(request: Request, key_id: str):
    user_id = request.state.user_id
    if not user_id:
        return JSONResponse({"detail": "Missing user_id"}, status_code=400)

    try:
        key = await db_client.get_api_key(api_key_id=key_id)
    except NotFound:
        return JSONResponse({"detail": "API key not found"}, status_code=404)
    except Banned:
        # key is banned — we still need to access it to unban
        pass

    # re-fetch without ban check to get the actual object
    from sqlalchemy import select
    from app.database.models.ApiKeys import ApiKey

    async with db_client.async_session() as dbsession:
        result = await dbsession.execute(
            select(ApiKey).where(ApiKey.id == key_id)
        )
        key = result.scalar_one_or_none()

    if not key:
        return JSONResponse({"detail": "API key not found"}, status_code=404)

    if str(key.user_id) != str(user_id):
        return JSONResponse({"detail": "Access denied"}, status_code=403)

    new_state = not bool(key.banned)
    await db_client.update_api_key(key_id=key_id, banned=new_state)

    return JSONResponse(
        {"detail": "updated", "banned": new_state}, status_code=200
    )
