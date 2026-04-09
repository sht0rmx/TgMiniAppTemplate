import asyncio
import logging
import os
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Header, Request
from fastapi.responses import JSONResponse
from sqlalchemy import update

from app.database.database import NotFound, db_client
from app.database.models.Users import User as UserModel
from app.middleware.auth import require_auth, require_origin
from app.services.auth.AuthService import AuthUtils
from app.services.auth.YandexOAuthService import YandexOAuthService
from app.schemas.models import LinkYandexRequest
from app.utils import create_hash, gen_code, parse_expire

logger = logging.getLogger("uvicorn.error")

router = APIRouter(prefix="/account", tags=["account"])


@router.post("/link/telegram/token", dependencies=[Depends(require_auth)])
async def get_telegram_linking_token(request: Request):
    """Generate a token for linking Telegram account."""
    user_id = request.state.user_id
    
    if not user_id:
        return JSONResponse({"detail": "Unauthorized"}, status_code=401)
    
    try:
        # Generate unique token for this linking session
        token = str(uuid.uuid4())[:8].upper()
        
        # Store token temporarily in cache (e.g., in Redis)
        # For now, we'll return it and expect the client to use it
        # In production, this should be stored with expiration
        
        return JSONResponse({"token": token}, status_code=200)
    except Exception as e:
        logger.error(f"Error generating linking token: {e}")
        return JSONResponse({"detail": "Internal server error"}, status_code=500)


@router.post("/link/telegram", dependencies=[Depends(require_origin)])
async def link_telegram_account(
    request_data: dict,
    request: Request,
    user_agent: str = Header(default=""),
):
    """Link existing user with Telegram initData."""
    user_id = request.state.user_id
    
    if not user_id:
        return JSONResponse({"detail": "Unauthorized"}, status_code=401)
    
    try:
        init_data = request_data.get("initData", "")
        if not init_data:
            return JSONResponse({"detail": "Missing initData"}, status_code=400)
        
        # Parse and validate initData (reuse logic from login)
        from urllib.parse import parse_qs
        parsed = {k: v[0] for k, v in parse_qs(init_data).items()}
        
        # Update user with new Telegram data
        import json
        from app.schemas.models import User as TgUser
        from pydantic import ValidationError
        
        try:
            user_data = TgUser(**json.loads(parsed["user"]))
        except ValidationError:
            return JSONResponse({"detail": "Invalid Telegram data"}, status_code=400)
        
        # Update user - set linked_telegram flag
        async with db_client.async_session() as dbsession:
            user = await db_client.get_user(uid=str(user_id))
            await dbsession.execute(
                update(UserModel)
                .where(UserModel.id == user.id)
                .values(telegram_id=user_data.id, linked_telegram=True)
            )
            await dbsession.commit()
        
        return JSONResponse({"detail": "Telegram linked successfully"}, status_code=200)
        
    except Exception as e:
        logger.error(f"Error linking Telegram: {e}")
        return JSONResponse({"detail": "Internal server error"}, status_code=500)


@router.post("/link/yandex", dependencies=[Depends(require_auth)])
async def link_yandex_account(
    request_data: LinkYandexRequest,
    request: Request,
):
    """Link existing user with Yandex OAuth account."""
    user_id = request.state.user_id
    
    if not user_id:
        return JSONResponse({"detail": "Unauthorized"}, status_code=401)
    
    try:
        code = request_data.code
        if not code:
            return JSONResponse({"detail": "Missing authorization code"}, status_code=400)
        
        # Initialize Yandex OAuth service
        oauth_service = YandexOAuthService()
        
        # Authenticate with Yandex
        auth_result = await oauth_service.authenticate_user(code)
        if not auth_result:
            return JSONResponse(
                {"detail": "Failed to authenticate with Yandex"}, status_code=401
            )
        
        user_info = auth_result["user_info"]
        yandex_id = user_info.get("id")
        
        if not yandex_id:
            return JSONResponse({"detail": "Invalid Yandex response"}, status_code=400)
        
        async with db_client.async_session() as dbsession:
            user = await db_client.get_user(uid=str(user_id))
            await dbsession.execute(
                update(UserModel)
                .where(UserModel.id == user.id)
                .values(yandex_id=str(yandex_id), linked_yandex=True)
            )
            await dbsession.commit()
        
        return JSONResponse({"detail": "Yandex linked successfully"}, status_code=200)
        
    except ValueError as e:
        logger.error(f"Yandex OAuth configuration error: {e}")
        return JSONResponse({"detail": "OAuth service not configured"}, status_code=500)
    except Exception as e:
        logger.error(f"Error linking Yandex account: {e}")
        return JSONResponse({"detail": "Internal server error"}, status_code=500)


@router.post("/unlink/{provider}", dependencies=[Depends(require_auth)])
async def unlink_account(
    provider: str,
    request: Request,
):
    """Unlink an OAuth account."""
    user_id = request.state.user_id
    
    if not user_id:
        return JSONResponse({"detail": "Unauthorized"}, status_code=401)
    
    if provider not in ["telegram", "yandex"]:
        return JSONResponse({"detail": "Invalid provider"}, status_code=400)
    
    try:
        user = await db_client.get_user(uid=str(user_id))
        
        if provider == "telegram":
            if not user.linked_yandex:
                return JSONResponse(
                    {"detail": "Cannot unlink your only authentication method"},
                    status_code=400
                )
        elif provider == "yandex":
            if not user.linked_telegram:
                return JSONResponse(
                    {"detail": "Cannot unlink your only authentication method"},
                    status_code=400
                )
        
        async with db_client.async_session() as dbsession:
            if provider == "telegram":
                await dbsession.execute(
                    update(UserModel)
                    .where(UserModel.id == user.id)
                    .values(linked_telegram=False)
                )
            elif provider == "yandex":
                await dbsession.execute(
                    update(UserModel)
                    .where(UserModel.id == user.id)
                    .values(linked_yandex=False, yandex_id=None)
                )
            
            await dbsession.commit()
        
        return JSONResponse(
            {"detail": f"{provider} unlinked successfully"}, status_code=200
        )
        
    except NotFound:
        return JSONResponse({"detail": "User not found"}, status_code=404)
    except Exception as e:
        logger.error(f"Error unlinking {provider}: {e}")
        return JSONResponse({"detail": "Internal server error"}, status_code=500)


@router.delete("", dependencies=[Depends(require_auth)])
async def delete_account(request: Request):
    """Delete user account permanently."""
    user_id = request.state.user_id
    
    if not user_id:
        return JSONResponse({"detail": "Unauthorized"}, status_code=401)
    
    try:
        await db_client.delete_user(user_id=str(user_id))
        return JSONResponse({"detail": "Account deleted successfully"}, status_code=200)
    except NotFound:
        return JSONResponse({"detail": "User not found"}, status_code=404)
    except Exception as e:
        logger.error(f"Error deleting account: {e}")
        return JSONResponse({"detail": "Internal server error"}, status_code=500)
